import yaml
from os import path as osp


class Config(object):
    def _parse_yaml_error(self, exc):
        print("Error while parsing YAML config file:")
        if hasattr(exc, "problem_mark"):
            if exc.context is not None:
                print(
                    "  parser says\n"
                    + "  {}\n".format(str(exc.problem_mark))
                    + "  {} {}\n".format(exc.problem, exc.context)
                    + "  Please correct data and retry."
                )
            else:
                print(
                    "  parser says\n"
                    + "  {}\n".format(str(exc.problem_mark))
                    + "  {}\n".format(str(exc.problem))
                    + "  Please correct data and retry."
                )
        else:
            print("Something went wrong while parsing yaml file")

    def _read_config(self, filename):
        try:
            with open(filename, "r") as f:
                read_config = yaml.load(f.read(), yaml.SafeLoader)
        except yaml.YAMLError as e:
            self._parse_yaml_error(e)
            raise e
        except IOError as e:
            print("Error while opening config file: {}".format(e))
            raise e
        return read_config

    def __init__(
        self,
        config_dir=None,
        config_file="config.yml",
    ):

        # Look for config file
        default_config_dirs = [  # Where to look for config file
            osp.dirname(osp.realpath(__file__)),
            "/etc/dacc",
        ]

        if config_dir is not None:
            # Look for config file in given directory
            if not osp.isfile(osp.join(config_dir, config_file)):
                raise ValueError(
                    "Config file not found in {}".format(
                        osp.join(config_dir, config_file)
                    )
                )
        else:
            # Look for config file in default directories
            try:
                config_dir = next(
                    dirname
                    for dirname in default_config_dirs
                    if osp.isfile(osp.join(dirname, config_file))
                )
            except StopIteration:
                raise ValueError(
                    "No {} config file could be found."
                    " Tried: {}".format(
                        config_file, ", ".join(default_config_dirs)
                    )
                )

        # Load config file
        config_fullpath = osp.join(config_dir, config_file)
        if not osp.isfile(config_fullpath):
            raise ValueError(
                "config file not found: {}".format(config_fullpath)
            )
        self._config = self._read_config(config_fullpath)

        # Validate config
        db_config = self.get("database")
        if not isinstance(db_config, dict):
            raise ValueError("database config should be a dict")
        for key in ["host", "port", "dbname", "user", "password"]:
            if key not in db_config:
                raise ValueError(
                    "Missing critical database parameter {} in DB config".format(
                        key
                    )
                )

        # Set flask config variables
        self.SQLALCHEMY_DATABASE_URI = (
            "postgresql://{user}:{password}@{host}:{port}/{database}".format(
                user=db_config.get("user"),
                password=db_config.get("password"),
                host=db_config.get("host"),
                port=db_config.get("port"),
                database=db_config.get("dbname"),
            )
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

    def get(self, key, default=None):
        """This method allows you to search a config value by its path
        using `:` as namespace delimiter
        """
        keys = key.split(":")
        search_base = self._config
        for searchkey in keys[:-1]:
            search_base = search_base.get(searchkey, {})
        return search_base.get(keys[-1], default)
