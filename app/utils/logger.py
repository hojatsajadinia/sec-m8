import logging
import sys


class Logger:
    def __init__(self, name="sec-m8", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.propagate = False

    def get_logger(self):
        return self.logger


# Usage:
# my_logger = Logger().get_logger()
# my_logger.info("This is an info message")
