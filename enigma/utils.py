import logging
import os
import sys

LOG_FORMAT = "%(levelname)-5s | %(asctime)s | %(module)s:%(funcName)s:%(lineno)-3s | %(message)s"
DT_FORMAT = "%H:%M:%S"


VERBOSE = 5
SPAM = 3
BARF = 2
logging.addLevelName(VERBOSE, "VERBOSE")
logging.addLevelName(SPAM, "SPAM")
logging.addLevelName(BARF, "BARF")
LOG_LEVEL = os.environ.get("LOG_LEVEL", default="INFO")


def get_logger(name: str, level: str = LOG_LEVEL) -> logging.Logger:

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DT_FORMAT)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    return logger


def spaces(n: int):
    return "".join([" "] * n)
