from dotenv import load_dotenv

load_dotenv("./.env_dev")

from set_version import VERSION
from spectacles.webapp.run import create_app

__version__ = VERSION

app = create_app(version=__version__)

try:

    app.run()

except Exception:

    raise
