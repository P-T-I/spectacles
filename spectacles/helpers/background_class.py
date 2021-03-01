import logging
import time

from spectacles.docker_reg_api.Docker_reg_api import DockerRegistryApi
from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import registry, namespaces, repository
from spectacles.webapp.run import db

logging.setLoggerClass(AppLogger)


class BackgroundTasks(object):
    def __init__(self):
        self.task_list = ["UpdateRegistryRepos"]
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting scheduled tasks")

        for each in self.task_list:
            getattr(self, each)()

        self.logger.info("Finished scheduled tasks run")

    def UpdateRegistryRepos(self):
        self.logger.info("Running UpdateRegistryRepos")

        from spectacles.webapp.run import create_app

        app = create_app(version="init")

        app.app_context().push()

        registries = registry.query.filter().all()

        # loop through configured registries
        for each in registries:
            dr = DockerRegistryApi(
                address=(each.uri.split(":")[0], each.uri.split(":")[1]),
                protocol=each.protocol,
                docker_service_name=each.service_name,
            )

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
                        .filter(namespaces.registryid == each.id)
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
                            my_repo.updated = int(time.time())
                            db.session.add(my_repo)
                        else:
                            db.session.add(
                                repository(
                                    name=name,
                                    path=repo,
                                    namespacesid=ns.id,
                                    created=int(time.time()),
                                )
                            )
                        db.session.commit()
                    # non-existing namespace
                    else:
                        self.logger.warning(
                            "Encountered a namespace on the registry that is not a part of spectacles namespace "
                            "database: {}. If you would like to access this namespace you will have to add it!".format(
                                namespace
                            )
                        )
        print()
