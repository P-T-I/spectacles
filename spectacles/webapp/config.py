import os
import ast


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


class Config(object):
    DEBUG = getenv_bool("DEBUG", "False")

    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_BACKEND = os.getenv("DB_BACKEND", "mysql")

    SQLALCHEMY_TRACK_MODIFICATIONS = getenv_bool("SQLALCHEMY_TRACK_MODIFICATIONS", "False")

    if DB_BACKEND == "mysql":
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI", "sqlite:////app/data/db/spectacles.db"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:////app/data/db/spectacles.db"

    AVATARS_SAVE_PATH = os.getenv("AVATARS_SAVE_PATH", "/app/data/avatars/")

    SPECTACLES_PRIV_KEY_PATH = os.getenv("SPECTACLES_PRIV_KEY_PATH", "/app/data/certs/domain.key")
    SPECTACLES_ISSUER_NAME = os.getenv("SPECTACLES_ISSUER_NAME", "Auth service")

    SPECTACLES_BACKGROUND_UPDATE = os.getenv("SPECTACLES_BACKGROUND_UPDATE", 30)

    SPECTACLES_WEB_TLS_KEY_PATH = os.getenv("SPECTACLES_WEB_TLS_KEY_PATH", "/app/certs/key.pem")
    SPECTACLES_WEB_TLS_CERT_PATH = os.getenv("SPECTACLES_WEB_TLS_CERT_PATH", "/app/certs/cert.pem")

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

    SQL_DEBUG_LOGGING = getenv_bool("SQL_DEBUG_LOGGING", "False")

    PROPAGATE_EXCEPTIONS = getenv_bool("PROPAGATE_EXCEPTIONS", "True")

    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "spectacles.session")
    SESSION_COOKIE_SECURE = getenv_bool("SESSION_COOKIE_SECURE", "True")
    SESSION_COOKIE_HTTPONLY = getenv_bool("SESSION_COOKIE_HTTPONLY", "True")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/log/")
    LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "spectacles.log")

    SYSLOG_ENABLE = getenv_bool("SYSLOG_ENABLE", "False")
    SYSLOG_SERVER = os.getenv("SYSLOG_SERVER", "172.16.1.1")
    SYSLOG_PORT = os.getenv("SYSLOG_PORT", "5140")
