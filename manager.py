from flask_script import Manager

from set_version import VERSION
from spectacles.webapp.run import create_app

__version__ = VERSION

app = create_app(version=__version__)

manager = Manager(app)


@manager.command
def runserver():
    app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))


@manager.command
def runworker():
    app.run(debug=False)


if __name__ == "__main__":
    manager.run()
