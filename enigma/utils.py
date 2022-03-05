import os


def vprint(message: str, msg_level: int, v_level: int = None):
    if v_level is None:
        v_level = int(os.getenv("verbosity", default="0"))
    if msg_level <= v_level:
        print(message)