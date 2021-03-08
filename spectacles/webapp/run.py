import logging
import random
import time
from hashlib import sha1

from flask import Flask, render_template
from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.config import Config
from spectacles.webapp.helpers.utils.times import timestampTOdatetimestring

logging.setLoggerClass(AppLogger)

fa = FontAwesome()
bootstrap = Bootstrap()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
avatars = Avatars()

config = Config()

if config.OPENID_LOGIN:
    from flask_oidc import OpenIDConnect

    oidc = OpenIDConnect()


def create_app(version):
    app = Flask(__name__, instance_relative_config=True)

    app.config["version"] = " v{}".format(version)

    app.config["SECRET_KEY"] = str(random.getrandbits(256))

    app.config.from_object(config)

    fa.init_app(app)
    bootstrap.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    avatars.init_app(app)

    if config.OPENID_LOGIN:
        oidc.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page!!!"
    login_manager.login_view = "auth.func_login"
    login_manager.session_protection = "strong"

    from spectacles.webapp.home import home as home_blueprint

    app.register_blueprint(home_blueprint)

    from spectacles.webapp.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from spectacles.webapp.token_auth import token_auth as token_auth_blueprint

    app.register_blueprint(token_auth_blueprint)

    from spectacles.webapp.admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint)

    from spectacles.webapp.errors import errors as error_blueprint

    app.register_blueprint(error_blueprint)

    if config.MYSQL_DEBUG_LOGGING:

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            statement_hash = sha1(statement.encode("utf-8")).hexdigest()[-6:]
            conn.info.setdefault("query_start_time", []).append(time.time())
            conn.info.setdefault("statement_hash", []).append(statement_hash)
            app.logger.debug("Start Query [{}]: {}".format(statement_hash, statement))

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            statement_hash = conn.info["statement_hash"].pop(-1)
            total = time.time() - conn.info["query_start_time"].pop(-1)
            app.logger.debug(
                "Query Complete [%s]: Total Time: %f", statement_hash, total
            )

    @app.context_processor
    def version():
        def get_version():
            return app.config["version"]

        return dict(get_version=get_version)

    @app.context_processor
    def TSToDatetime():
        def TSToDatetime(ts):
            return timestampTOdatetimestring(ts)

        return dict(TSToDatetime=TSToDatetime)

    @app.errorhandler(403)
    def forbidden(error):
        return (
            render_template(
                "errors/403.html",
                header="Forbidden",
                authenticated=current_user.is_authenticated,
                error=True,
            ),
            403,
        )

    @app.errorhandler(404)
    def page_not_found(error):
        return (
            render_template(
                "errors/404.html",
                header="Page Not Found",
                authenticated=current_user.is_authenticated,
                error=True,
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            render_template(
                "errors/500.html",
                header="Internal Server Error",
                authenticated=current_user.is_authenticated,
                error=True,
            ),
            500,
        )

    return app
