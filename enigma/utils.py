import logging
import os
import sys

LOG_FORMAT = "%(levelname)-5s | %(asctime)s | %(module)s:%(lineno)s-3s | %(message)s"
DT_FORMAT = "%H:%M:%S"

def vprint(message: str, msg_level: int, v_level: int = None):
    if v_level is None:
        v_level = int(os.getenv("verbosity", default="0"))
    if msg_level <= v_level:
        print(message)

logging.addLevelName(5, "VERBOSE")
VERBOSE = 5


def get_logger(name: str, level: str = "DEBUG") -> logging.Logger:

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DT_FORMAT)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    return logger
