import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined

__all__ = ["env"]
__curdir__ = os.path.dirname(os.path.realpath(__file__))

env = Environment(
    loader=FileSystemLoader(os.path.join(__curdir__, "templates")),
    undefined=StrictUndefined
)
