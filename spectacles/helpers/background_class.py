import logging

from spectacles.docker_reg_api.Docker_reg_api import DockerRegistryApi
from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import registry

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
        api_list = []
        for each in registries:
            api_list.append(
                DockerRegistryApi(
                    address=(each.uri.split(":")[0], each.uri.split(":")[1]),
                    protocol=each.protocol,
                    docker_service_name=each.service_name,
                )
            )

        print()
