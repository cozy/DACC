import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    DB_NAME = os.environ.get('DB_NAME') or 'dacc'
    DB_USER = os.environ.get('DB_USER') or 'paul'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'paul'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    