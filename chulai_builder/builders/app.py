import logging

from .paas import paas
from .build import RailsBuild


logger = logging.getLogger(__name__)


FACTORY = dict(
    rails=RailsBuild
)


def get_builder(builder_type):
    builder = FACTORY.get(builder_type)
    if builder is None:
        raise ValueError(
            "no suitable builder for: {0}".format(builder_type)
        )
    return builder


class App(object):
    def __init__(self, name, app_type, repo, base_image, current, config):
        self._name = name
        self._app_type = app_type
        self._repo = repo
        self._config = config
        self._base_image = base_image
        self._current = current

    @property
    def name(self):
        return self._name

    @property
    def app_type(self):
        return self._app_type

    @property
    def repo(self):
        return "".join(["git@", paas.git, ":", self._repo, ".git"])

    @property
    def config(self):
        return self._config

    @property
    def base_image(self):
        return self._base_image

    @property
    def current(self):
        return self._current

    @property
    def tag_name(self):
        """
        env_name = reg-name/base-img:tag ==> base-img-tag
        tag_name = app-name-env-name
        """
        splited = self._base_image.split("/")
        if len(splited) == 1:
            reg_name = ""
            env_name = splited[0]
        elif len(splited) == 2:
            reg_name, env_name = splited
            reg_name = reg_name + "/"
        else:
            raise ValueError("invalid base image format")

        for ori in ":._":
            env_name = env_name.replace(ori, "-")

        return "{0}{1}-{2}".format(reg_name, self.name, env_name)

    def new_build(self, commit):
        Builder = get_builder(self.app_type)
        return Builder(self, commit)
