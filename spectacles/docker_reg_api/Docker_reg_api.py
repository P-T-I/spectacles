import ast
from urllib.parse import parse_qs

import requests

from spectacles.helpers.generic_api import GenericApi
from spectacles.webapp.helpers.objects.token_class import Token


class DockerRegistryApi(GenericApi):
    def __init__(
        self,
        address,
        api_path="v2",
        proxies=None,
        protocol="https",
        user_agent="Spectacles",
        docker_service_name=None,
    ):
        self.address = address
        self.api_path = api_path
        self.proxies = proxies
        self.protocol = protocol
        self.user_agent = user_agent

        self.docker_service_name = docker_service_name

        super().__init__(
            self.address, self.api_path, self.proxies, self.protocol, self.user_agent
        )

    def fetch_token(self, scope, service):
        token = Token(
            account="Spectacles",
            client_id="Spectacles",
            scope=scope,
            offline_token=True,
            service=service,
        )

        return token

    def set_token_header(self, name, action="pull"):

        token = self.fetch_token(
            f"repository:{name}:{action}", service=self.docker_service_name
        )

        self.set_header_field("Authorization", f"Bearer {token.build_token()['token']}")

    def ping(self):

        resource = ""

        requests.packages.urllib3.disable_warnings()

        request_api_resource = {
            "headers": self.myheaders,
            "verify": self.verify,
            "timeout": 60,
            "proxies": self.proxies,
        }

        with self.get_session() as session:
            r = session.get(
                f"{self.baseurl}/{self.api_path}/{resource}", **request_api_resource
            )

            if "Www-Authenticate" in r.headers:
                auth_header = r.headers["Www-Authenticate"]

                auth_header = auth_header.replace("Bearer ", "").replace(",", "&")

                dict_headers = parse_qs(auth_header)

                ret_dict = {
                    "service": ast.literal_eval(dict_headers["service"][0]),
                    "auth_token_uri": ast.literal_eval(dict_headers["realm"][0]),
                }

                token = self.fetch_token("registry:catalog:*", ret_dict["service"])

                self.set_header_field(
                    "Authorization", f"Bearer {token.build_token()['token']}"
                )

                resource = "_catalog"

                r = session.get(
                    f"{self.baseurl}/{self.api_path}/{resource}", **request_api_resource
                )

                if r.status_code == 200:
                    return ret_dict
                else:
                    return False
            else:
                return False

    def catalog_registry(self):

        token = self.fetch_token("registry:catalog:*", service=self.docker_service_name)

        self.set_header_field("Authorization", f"Bearer {token.build_token()['token']}")

        resource = "_catalog"

        return self.call("GET", resource=resource)

    def get_repository_list(self, name):

        self.set_token_header(name=name)

        resource = f"{name}/tags/list"

        return self.call("GET", resource=resource)

    def get_repository_digest(self, name, tag):

        self.set_header_field(
            "Accept", "application/vnd.docker.distribution.manifest.v2+json"
        )

        self.set_token_header(name=name)

        resource = f"{name}/manifests/{tag}"

        result = self.call("GET", resource=resource, ret_headers=True)

        return result["Docker-Content-Digest"]

    def delete_repository(self, name, digest):

        self.set_token_header(name=name, action="delete")

        resource = f"{name}/manifests/{digest}"

        return self.call("DELETE", resource=resource)
