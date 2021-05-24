import yaml
import sys


class Config(object):

    try:
        with open("config.yml", "r") as config:
            cfg = yaml.load(config, Loader=yaml.FullLoader)
            db = cfg["database"]
            SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
                db["user"], db["password"], db["host"], db["port"], db["name"])
            SQLALCHEMY_TRACK_MODIFICATIONS = False

    except Exception as err:
        print("Error while opening config.yaml: " + repr(err))
        sys.exit()
