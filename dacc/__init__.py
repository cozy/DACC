from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

dacc = Flask(__name__)
dacc.config.from_object(Config)

db = SQLAlchemy(dacc)

from dacc import routes, models
from dacc.cli import db
