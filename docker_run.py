from spectacles.webapp.run import create_app
from set_version import VERSION

__version__ = VERSION

app = create_app(version=__version__)
