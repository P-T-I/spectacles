import logging
import time

from spectacles.docker_reg_api.Docker_reg_api import DockerRegistryApi
from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import registry, namespaces, repository, tags
from spectacles.webapp.run import db

logging.setLoggerClass(AppLogger)


class BackgroundTasks(object):
    def __init__(self, app):
        self.task_list = ["UpdateRegistryRepos"]

        self.app = app

        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting scheduled tasks")

        for each in self.task_list:
            getattr(self, each)()

        self.logger.info("Finished scheduled tasks run")

    def UpdateRegistryRepos(self):
        self.logger.info("Running UpdateRegistryRepos")

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
                            else:
                                my_repo = repository(
                                    name=name,
                                    path=repo,
                                    namespacesid=ns.id,
                                    created=int(time.time()),
                                    updated=update_time,
                                )

                            db.session.add(my_repo)
                            db.session.commit()

                            repo_list = dr.get_repository_list(name=repo)

                            if "tags" in repo_list:
                                if repo_list["tags"] is not None and isinstance(
                                    repo_list["tags"], list
                                ):
                                    for tag in repo_list["tags"]:

                                        self.logger.info(
                                            "Processing tag: {} of repo: {}".format(
                                                tag, repo
                                            )
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

                                        self.logger.info("{}".format(my_tag))

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

                                        db.session.add(my_tag)
                                        db.session.commit()
                                elif repo_list["tags"] is None:
                                    # this repository is deleted; remove from the database
                                    repository.query.filter(
                                        repository.id == my_repo.id
                                    ).delete()
                                    db.session.commit()

                        # non-existing namespace
                        else:
                            self.logger.warning(
                                "Encountered a namespace on the registry that is not a part of spectacles namespace "
                                "database: {}. If you would like to access this namespace you will have to add it!".format(
                                    namespace
                                )
                            )

                # deleting tags that are not updated; assuming that they do not longer exist on the registry
                tags.query.filter(tags.updated != update_time).delete()
                db.session.commit()

                # deleting repositories that are not updated; assuming that they do not longer exist on the
                # registry
                repository.query.filter(repository.updated != update_time).delete()
                db.session.commit()
