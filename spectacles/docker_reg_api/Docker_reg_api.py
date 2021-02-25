import ast
import json
from urllib.parse import parse_qs

import requests

from spectacles.helpers.generic_api import GenericApi
from spectacles.webapp.helpers.objects.token_class import Token


class DockerRegistryApi(GenericApi):

    def __init__(
            self, address, api_path="v2", proxies=None, protocol="https", user_agent="Spectacles",
    ):
        self.address = address
        self.api_path = api_path
        self.proxies = proxies
        self.protocol = protocol
        self.user_agent = user_agent

        super().__init__(
            self.address, self.api_path, self.proxies, self.protocol, self.user_agent,
        )

    def ping(self):

        resource = "/"

        requests.packages.urllib3.disable_warnings()

        request_api_resource = {
            "headers": self.myheaders,
            "verify": self.verify,
            "timeout": 60,
            "proxies": self.proxies,
        }

        with self.get_session() as session:
            r = session.get("{0}/{1}/{2}".format(self.baseurl, self.api_path, resource), **request_api_resource)

            if "Www-Authenticate" in r.headers:
                auth_header = r.headers["Www-Authenticate"]

                auth_header = auth_header.replace("Bearer ", "").replace(",", "&")

                dict_headers = parse_qs(auth_header)

                ret_dict = {
                    "service": ast.literal_eval(dict_headers["service"][0]),
                    "auth_token_uri": ast.literal_eval(dict_headers["realm"][0])
                }

                data = {
                    "username": "foo",
                    "password": "bar",
                    "service": ret_dict["service"]
                }

                request_api_resource = {
                    "data": json.dumps(data),
                    "headers": self.myheaders,
                    "verify": self.verify,
                    "timeout": 60,
                    "proxies": self.proxies,
                }

                token = session.post(ret_dict["auth_token_uri"], **request_api_resource)

                return ret_dict

            else:
                return False
