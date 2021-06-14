import sentry_sdk
from config import Config
from dacc.version import __version__
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_migrate import Migrate

configdata = Config()
dacc = Flask(__name__)
dacc.config.from_object(configdata)
dacc.version = __version__

sentry_config = configdata.get("sentry", {})
sentry_sdk.init(
    dsn=configdata.get("sentry:dsn", ""),
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=configdata.get("sentry:traces_sample_rate", 1.0),
    release="dacc@{}".format(__version__),
)

dacc_token = configdata.get("auth:token", {})

db = SQLAlchemy(dacc)
migrate = Migrate(dacc, db)

from dacc import routes, models  # noqa: E402 F401
from dacc.cli import cli  # noqa: E402 F401
