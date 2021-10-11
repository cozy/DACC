import logging
import logging.handlers


class Logger(object):
    def __init__(self, config):
        self.config = config
        if self.config.get("enable", False):
            # Configure syslog handler
            handler = logging.handlers.SysLogHandler(address="/dev/log")
            format = "%(name)s[%(process)s]: %(message)s"
            formatter = logging.Formatter(format, datefmt="%b %d %H:%M:%S")
            handler.setFormatter(formatter)

            # Configure logger
            self.logger = logging.getLogger("dacc")
            logger_criticity = config.get("logging", {}).get(
                "logger_criticity", "debug"
            )
            threshold = getattr(logging, logger_criticity.upper())
            self.logger.setLevel(threshold)
            self.logger.addHandler(handler)
            self.logger.debug("DACC started")

    def log(self, level, message):
        if not self.config.get("enable", False):
            return
        loglevel = getattr(logging, level.upper())
        self.logger.log(loglevel, message)
