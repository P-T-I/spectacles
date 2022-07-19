import base64
import hashlib
import json
import time
import uuid

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)

from spectacles.webapp.app.models import users, namespaces, claims, claimsgroups
from spectacles.webapp.config import Config
from spectacles.webapp.helpers.constants.rights import repo_rights
from spectacles.webapp.helpers.utils.times import timestampTOdatetimestring
from spectacles.webapp.run import db


class Token(object):
    def __init__(
        self, account=None, client_id=None, scope=None, offline_token=None, service=None
    ):

        self.config = Config()

        self.jwt_id = uuid.uuid4().hex
        self.private_key = self.__get_priv_key()
        self.public_key = self.private_key.public_key()

        self.account = account
        self.client_id = client_id
        self.scope = scope

        if self.scope is not None:
            (
                self.scope_type,
                self.scope_name,
                self.scope_namespace,
                self.scope_actions,
            ) = self.split_scope()

        self.offline_token = offline_token
        self.service = service

        self.issuer = self.config.SPECTACLES_ISSUER_NAME

        self.header = {"typ": "JWT", "alg": "RS256", "kid": self.get_kid()}

        if self.account == "Spectacles":
            self.claims = self.get_reg_claim()
        else:
            self.claims = self.get_claim()

        self.token = self.build_token()

    def __get_priv_key(self):
        with open(self.config.SPECTACLES_PRIV_KEY_PATH) as f:
            file = f.read()
        priv_key = load_pem_private_key(
            file.encode(), password=None, backend=default_backend()
        )

        return priv_key

    def get_kid(self):
        # reformat the public key to DER encoding
        pub_key_der = self.public_key.public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        )
        # get a sha256 hash
        pub_hash = hashlib.sha256(pub_key_der).digest()
        # get first 30 bytes (truncated to 240 bits) and base32 encode it
        payload = base64.b32encode(pub_hash[:30])

        payload = payload.decode("utf-8")
        kid = ":".join([payload[i : i + 4] for i in range(0, len(payload), 4)])

        return kid

    def split_scope(self):

        scope_list = self.scope.split(":")

        scope_type = scope_list[0]
        scope_name = scope_list[1]
        scope_actions = scope_list[2]

        if "," in scope_actions:
            scope_actions = scope_actions.split(",")
        else:
            scope_actions = [scope_actions]

        if "/" in scope_name:
            splits = scope_name.split("/")
            scope_namespace = splits[0]
        else:
            scope_namespace = "/"

        return scope_type, scope_name, scope_namespace, scope_actions

    def get_reg_claim(self):

        return {
            "iss": self.issuer,
            "sub": self.account if self.account is not None else self.client_id,
            "aud": self.service,
            "exp": int(time.time()) + 900,
            "nbf": int(time.time()) - 30,
            "iat": int(time.time()),
            "jti": self.jwt_id,
            "access": [
                {
                    "type": self.scope_type,
                    "name": self.scope_name,
                    "actions": self.scope_actions,
                }
            ],
        }

    def get_claim(self):

        if self.scope is None:
            # this is just a authentication request
            return {
                "iss": self.issuer,
                "sub": self.account if self.account is not None else self.client_id,
                "aud": self.service,
                "exp": int(time.time()) + 900,
                "nbf": int(time.time()) - 30,
                "iat": int(time.time()),
                "jti": self.jwt_id,
                "access": [],
            }

        else:
            return {
                "iss": self.issuer,
                "sub": self.account if self.account is not None else self.client_id,
                "aud": self.service,
                "exp": int(time.time()) + 900,
                "nbf": int(time.time()) - 30,
                "iat": int(time.time()),
                "jti": self.jwt_id,
                "access": [self.fetch_user_authorizations()],
            }

    def __check_write_only(self, claim):
        the_rights = getattr(repo_rights, claim)
        if set(the_rights).issubset(set(self.scope_actions)):
            return getattr(repo_rights, "FULL")
        else:
            return getattr(repo_rights, claim)

    def fetch_user_authorizations(self):
        action_dict = {"type": self.scope_type, "name": self.scope_name, "actions": []}

        # get the user
        user = users.query.filter(users.username == self.account).first()

        req_ns = namespaces.query.filter(
            namespaces.name == self.scope_namespace
        ).first()

        if user is None:
            # containerd doesn't forward a user in request, return read only rights
            action_dict["actions"] = getattr(repo_rights, "READ")
            return action_dict
        else:
            # check if user is admin
            if user.status == 99 or user.role == "admin":
                # admins have full rights by default
                action_dict["actions"] = getattr(repo_rights, "FULL")
                return action_dict

        # first check for specific user claims
        user_claims = [
            x.claims for x in user.claimmembers if x.claims.namespaceid == req_ns.id
        ]
        if len(user_claims):
            if user_claims[0].claim == "WRITE":
                action_dict["actions"] = self.__check_write_only(user_claims[0].claim)
                return action_dict
            else:
                action_dict["actions"] = getattr(repo_rights, user_claims[0].claim)
                return action_dict

        # check if namespace has group members
        if len(req_ns.members) != 0:
            # check if user is part of namespace
            usr_ns = [x.userid for x in req_ns.members if x.userid == user.id]

            if len(usr_ns) != 0:
                # check if user is namespace owner
                if req_ns.owner == user.id:
                    # owners have full rights by default
                    action_dict["actions"] = getattr(repo_rights, "FULL")
                    return action_dict
                else:
                    if req_ns.P_claim == "WRITE":
                        action_dict["actions"] = self.__check_write_only(req_ns.P_claim)
                        return action_dict
                    else:
                        # user privileges outweigh group privileges, so fetch namespace rights
                        action_dict["actions"] = getattr(repo_rights, req_ns.P_claim)
                        return action_dict

        # check for specific group claims
        if len(user.group_member) != 0:
            # fetch all user groups
            grps = [x.groupid for x in user.group_member]

            grp_claims = claims.query.filter(
                claims.id.in_(
                    db.session.query(claimsgroups.claimsid)
                    .filter(claimsgroups.groupid.in_(grps))
                    .all()
                )
            ).all()

            if len(grp_claims) != 0:
                if grp_claims[0].claim == "WRITE":
                    action_dict["actions"] = self.__check_write_only(
                        grp_claims[0].claim
                    )
                    return action_dict
                else:
                    action_dict["actions"] = getattr(repo_rights, grp_claims[0].claim)
                    return action_dict

        # check if namespace has group members
        if len(req_ns.groups) != 0:
            # check if user has memberships to groups
            if len(user.group_member) != 0:
                # fetch all user groups id's
                grp_ids = [x.groupid for x in user.group_member]
                # fetch namespace group ids
                ns_grp_ids = [x.groupid for x in req_ns.groups]
                # check for an overlap between the two
                if len(set(grp_ids).intersection(set(ns_grp_ids))) != 0:
                    if req_ns.G_claim == "WRITE":
                        action_dict["actions"] = self.__check_write_only(req_ns.G_claim)
                        return action_dict
                    else:
                        action_dict["actions"] = getattr(repo_rights, req_ns.G_claim)
                        return action_dict

        # check for namespace 'other' rights if some other then 'NONE'
        if req_ns.O_claim != "NONE":
            if req_ns.O_claim == "WRITE":
                action_dict["actions"] = self.__check_write_only(req_ns.O_claim)
                return action_dict
            else:
                action_dict["actions"] = getattr(repo_rights, req_ns.O_claim)
                return action_dict

        # if we make it this far; the user has no rights; return empty action list
        return action_dict

    def get_payload(self):
        b64_header = (
            base64.urlsafe_b64encode(json.dumps(self.header).replace(" ", "").encode())
            .decode("utf-8")
            .rstrip("=")
        )
        b64_claims = (
            base64.urlsafe_b64encode(json.dumps(self.claims).replace(" ", "").encode())
            .decode("utf-8")
            .rstrip("=")
        )

        payload = f"{b64_header}.{b64_claims}"

        return payload

    def build_token(self):

        return {
            "token": jwt.encode(
                self.claims, self.private_key, algorithm="RS256", headers=self.header
            ),
            "expires_in": 900,
            "issued_at": timestampTOdatetimestring(int(time.time())),
        }
