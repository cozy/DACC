from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy


configdata = Config()
dacc = Flask(__name__)
dacc.config.from_object(configdata)

db = SQLAlchemy(dacc)

from dacc import routes, models
