import os
import ast
import random


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


class Config(object):
    DEBUG = getenv_bool("DEBUG", "False")

    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_BACKEND = os.getenv("DB_BACKEND", "mysql")

    WEB_ROOT = os.getenv("WEB_ROOT", "")

    SECRET_KEY = os.getenv("SECRET_KEY", str(random.getrandbits(256)))

    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "spectacles")
    MYSQL_USER = os.getenv("MYSQL_USER", "spectacles")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}/{MYSQL_DATABASE}",
    )

    AVATARS_SAVE_PATH = os.getenv("AVATARS_SAVE_PATH", "/app/data/avatars/")

    SPECTACLES_PRIV_KEY_PATH = os.getenv(
        "SPECTACLES_PRIV_KEY_PATH", "/app/data/certs/domain.key"
    )
    SPECTACLES_ISSUER_NAME = os.getenv("SPECTACLES_ISSUER_NAME", "Auth service")

    SPECTACLES_BACKGROUND_UPDATE = os.getenv("SPECTACLES_BACKGROUND_UPDATE", 30)

    SPECTACLES_WEB_TLS_KEY_PATH = os.getenv(
        "SPECTACLES_WEB_TLS_KEY_PATH", "/app/certs/key.pem"
    )
    SPECTACLES_WEB_TLS_CERT_PATH = os.getenv(
        "SPECTACLES_WEB_TLS_CERT_PATH", "/app/certs/cert.pem"
    )

    OPENID_LOGIN = getenv_bool("OPENID_LOGIN", "False")

    OIDC_CLIENT_SECRETS = os.getenv("OIDC_CLIENT_SECRETS", "client_secrets.json")
    OIDC_ID_TOKEN_COOKIE_SECURE = getenv_bool("OIDC_ID_TOKEN_COOKIE_SECURE", "False")
    OIDC_REQUIRE_VERIFIED_EMAIL = getenv_bool("OIDC_REQUIRE_VERIFIED_EMAIL", "False")
    OIDC_USER_INFO_ENABLED = getenv_bool("OIDC_USER_INFO_ENABLED", "True")
    OIDC_OPENID_REALM = os.getenv("OIDC_OPENID_REALM", "spectacles")
    OIDC_SCOPES = os.getenv("OIDC_SCOPES", ["openid"])
    OIDC_INTROSPECTION_AUTH_METHOD = os.getenv(
        "OIDC_INTROSPECTION_AUTH_METHOD", "client_secret_post"
    )
    OIDC_VALID_ISSUERS = os.getenv("OIDC_VALID_ISSUERS", "https://OIDC_VALID_ISSUERS")
    OVERWRITE_REDIRECT_URI = os.getenv("OVERWRITE_REDIRECT_URI", False)
    OIDC_CALLBACK_ROUTE = os.getenv("OIDC_CALLBACK_ROUTE", "/oidc_callback")
    OIDC_ID_TOKEN_COOKIE_PATH = os.getenv("OIDC_ID_TOKEN_COOKIE_PATH", "/")
    OIDC_ID_TOKEN_COOKIE_NAME = os.getenv(
        "OIDC_ID_TOKEN_COOKIE_NAME", "spec_oidc_cookie"
    )

    SQL_DEBUG_LOGGING = getenv_bool("SQL_DEBUG_LOGGING", "False")

    PROPAGATE_EXCEPTIONS = getenv_bool("PROPAGATE_EXCEPTIONS", "True")

    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/log/")
    LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "spectacles.log")

    SYSLOG_ENABLE = getenv_bool("SYSLOG_ENABLE", "False")
    SYSLOG_SERVER = os.getenv("SYSLOG_SERVER", "172.16.1.1")
    SYSLOG_PORT = os.getenv("SYSLOG_PORT", "5140")

    REGISTER_ENABLED = getenv_bool("REGISTER_ENABLED", "False")
