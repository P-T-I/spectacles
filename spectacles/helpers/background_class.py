import logging
import time
import datetime

from spectacles.docker_reg_api.Docker_reg_api import DockerRegistryApi
from spectacles.helpers.activity_tracker import ActivityTracker
from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import (
    registry,
    namespaces,
    repository,
    tags,
    activity,
)
from spectacles.webapp.helpers.constants.common import action_types
from spectacles.webapp.helpers.utils.times import datetimeTOtimestamp
from spectacles.webapp.run import db

logging.setLoggerClass(AppLogger)


class BackgroundTasks(object):
    def __init__(self, app):
        self.task_list = ["UpdateRegistryRepos", "CleanUpActivities"]

        self.app = app

        self.activity = ActivityTracker(action_type=action_types.BG_PULL)

        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting scheduled tasks")

        for each in self.task_list:
            getattr(self, each)()

        self.logger.info("Finished scheduled tasks run")

    def CleanUpActivities(self):
        self.logger.info("Running CleanUpActivities")

        self.activity.info("Cleaning up activities...")

        # create timedelta object
        twelve_hour_timedelta = datetime.timedelta(hours=6)

        now = datetime.datetime.now()

        query_ts = datetimeTOtimestamp(now - twelve_hour_timedelta)

        with self.app.app_context():
            res = (
                db.session.query(activity)
                .filter(activity.log_time <= query_ts)
                .delete()
            )
            db.session.commit()
            if res != 0:
                self.activity.info(f"Deleted from past activities: {res} entries")

    def UpdateRegistryRepos(self):
        self.logger.info("Running UpdateRegistryRepos")

        self.activity.info("Checking for registry changes...")

        with self.app.app_context():

            registries = registry.query.filter().all()

            # loop through configured registries
            for register in registries:
                dr = DockerRegistryApi(
                    address=(register.uri.split(":")[0], register.uri.split(":")[1]),
                    protocol=register.protocol,
                    docker_service_name=register.service_name,
                )

                # set update time
                update_time = int(time.time())

                registry_catalog = dr.catalog_registry()
                if len(registry_catalog["repositories"]) != 0:
                    for repo in registry_catalog["repositories"]:
                        # check if repo is namespaced
                        if "/" in repo:
                            splits = repo.split("/")
                            namespace = splits[0]
                            name = splits[1]
                        else:
                            namespace = "/"
                            name = repo

                        ns = (
                            namespaces.query.filter(namespaces.name == namespace)
                            .filter(namespaces.registryid == register.id)
                            .first()
                        )
                        # existing namespace
                        if ns:
                            my_repo = (
                                repository.query.filter(repository.path == repo)
                                .filter(repository.namespacesid == ns.id)
                                .first()
                            )
                            if my_repo:
                                my_repo.updated = update_time
                                NEW = False
                            else:
                                my_repo = repository(
                                    name=name,
                                    path=repo,
                                    namespacesid=ns.id,
                                    created=int(time.time()),
                                    updated=update_time,
                                )
                                NEW = True

                            repo_list = dr.get_repository_list(name=repo)

                            if "tags" in repo_list:
                                if repo_list["tags"] is not None and isinstance(
                                    repo_list["tags"], list
                                ):
                                    if NEW:
                                        self.activity.success(
                                            f"New repository discovered: {my_repo.name}"
                                        )
                                    db.session.add(my_repo)
                                    db.session.commit()

                                    for tag in repo_list["tags"]:

                                        self.logger.info(
                                            f"Processing tag: {tag} of repo: {repo}"
                                        )

                                        digest = dr.get_repository_digest(
                                            name=repo, tag=tag
                                        )

                                        # check existing tag
                                        my_tag = (
                                            tags.query.filter(tags.version == tag)
                                            .filter(tags.repositoryid == my_repo.id)
                                            .first()
                                        )

                                        # existing tag
                                        if my_tag is not None:
                                            my_tag.digest = digest
                                            my_tag.updated = update_time
                                        # new tag
                                        else:
                                            my_tag = tags(
                                                version=tag,
                                                repositoryid=my_repo.id,
                                                digest=digest,
                                                created=int(time.time()),
                                                updated=update_time,
                                            )
                                            self.activity.success(
                                                f"New tag {my_tag.version} discovered for repository: {my_repo.name}"
                                            )

                                        db.session.add(my_tag)
                                        db.session.commit()

                                elif repo_list["tags"] is None:
                                    # this repository is deleted; remove from the database
                                    del_repo = repository.query.filter(
                                        repository.id == my_repo.id
                                    ).delete()
                                    db.session.commit()
                                    if del_repo != 0:
                                        self.activity.danger(
                                            f"Deleted repository: {my_repo.name}"
                                        )

                        # non-existing namespace
                        else:
                            log_string = (
                                "Encountered a namespace on the registry that is not a part of spectacles "
                                f"namespace database: {namespace}. If you would like to access this namespace you "
                                "will have to add it!"
                            )
                            self.logger.warning(log_string)
                            self.activity.warning(log_string)

                # deleting tags that are not updated; assuming that they do not longer exist on the registry
                del_tags = tags.query.filter(tags.updated != update_time).delete()
                db.session.commit()
                if del_tags != 0:
                    self.activity.info(f"Deleted {del_tags} old tags")

                # deleting repositories that are not updated; assuming that they do not longer exist on the
                # registry
                del_rep = repository.query.filter(
                    repository.updated != update_time
                ).delete()
                db.session.commit()
                if del_rep != 0:
                    self.activity.info(f"Deleted {del_tags} old tags")
