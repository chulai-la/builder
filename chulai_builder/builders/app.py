import logging
import os

from ..paas import paas

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
    def __init__(self, app_id, app_type, repo, base_image, current, env):
        self._app_id = app_id
        self._app_type = app_type
        self._repo = repo
        self._base_image = base_image
        self._current = current
        self._env = env

    @property
    def app_id(self):
        return self._app_id

    @property
    def app_type(self):
        return self._app_type

    @property
    def repo(self):
        return "".join(["git@", paas.git, ":", self._repo, ".git"])

    @property
    def env(self):
        return self._env.copy()

    @property
    def base_image(self):
        return "/".join([paas.docker_registry, self._base_image])

    @property
    def current(self):
        return self._current

    @property
    def tag_name(self):
        image_name = self.image_name.replace("/", "-")
        return "{0}/{1}".format(paas.docker_registry, image_name)

    @property
    def image_name(self):
        env_name = self._base_image
        for ori in ":._":
            env_name = env_name.replace(ori, "-")
        return "{0}/{1}".format(self.app_id, env_name)

    def get_build(self, commit):
        Builder = get_builder(self.app_type)
        return Builder(self, commit)

    @property
    def work_dir(self):
        # work dir in docker
        return os.path.join("/", "home", paas.user, self.app_id)

    @property
    def construction(self):
        """construction on builder host"""

    @property
    def playground(self):
        """playground on agent host"""
