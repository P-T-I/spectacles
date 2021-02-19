import base64
import hashlib
import json
import time
import uuid
import jwt

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)

from spectacles.webapp.helpers.utils.times import timestampTOdatetimestring


class Token(object):
    def __init__(self):
        self.jwt_id = uuid.uuid4().hex
        self.private_key = self.__get_priv_key()
        self.public_key = self.private_key.public_key()

        self.header = {"typ": "JWT", "alg": "ES256", "kid": self.get_kid()}

        self.token = self.build_token()

    @staticmethod
    def __get_priv_key():
        with open(
            "./registry_auth/certs/RootCA.key"
        ) as f:  # TODO convert this path to a variable....
            file = f.read()
        priv_key = load_pem_private_key(file.encode(), None)

        return priv_key

    def get_kid(self):
        # reformat the public key to DER encoding
        pub_key_der = self.public_key.public_bytes(Encoding.DER, PublicFormat.PKCS1)
        # get a sha256 hash
        pub_hash = hashlib.sha256(pub_key_der).hexdigest()
        # get first 30 bytes (truncated to 240 bits) and base32 encode it
        payload = base64.b32encode(pub_hash[:30].encode())

        payload = payload.decode("utf-8")
        kid = ":".join([payload[i: i + 4] for i in range(0, len(payload), 4)])

        return kid

    def get_claim(self):

        return {
            "iss": "DCSC_KEEPER_OF_TOKENS",
            "sub": "docker",
            "aud": "Authentication",
            "exp": int(time.time()) + 3600,
            "nbf": int(time.time()) - 30,
            "iat": int(time.time()),
            "jti": self.jwt_id,
            "access": [
                {
                    "type": "repository",
                    "name": "samalba/my-app",
                    "actions": ["pull", "push"],
                }
            ],
        }

    def build_token(self):

        # b64_header = (
        #     base64.urlsafe_b64encode(json.dumps(self.header).replace(" ", "").encode())
        #     .decode("utf-8")
        #     .rstrip("=")
        # )
        # b64_claims = (
        #     base64.urlsafe_b64encode(
        #         json.dumps(self.get_claim()).replace(" ", "").encode()
        #     )
        #     .decode("utf-8")
        #     .rstrip("=")
        # )
        #
        # cat_b64s = "{}.{}".format(b64_header, b64_claims)

        return {
            "token": jwt.encode(self.get_claim(), self.private_key, algorithm="RS256", headers=self.header),
            "expires_in": 3600,
            "issued_at": timestampTOdatetimestring(int(time.time())),
        }
