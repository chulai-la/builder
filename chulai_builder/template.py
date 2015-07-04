import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined

__all__ = ["get_env"]


def get_env(filepath):
    __curdir__ = os.path.dirname(os.path.realpath(filepath))
    env = Environment(
        loader=FileSystemLoader(os.path.join(__curdir__, "templates")),
        undefined=StrictUndefined
    )
    return env
