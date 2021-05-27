from flask import Flask
from config import Config
from dacc.version import __version__
from flask_sqlalchemy import SQLAlchemy


configdata = Config()
dacc = Flask(__name__)
dacc.config.from_object(configdata)
dacc.version = __version__

db = SQLAlchemy(dacc)

from dacc import routes, models
