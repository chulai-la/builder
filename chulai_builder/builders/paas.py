import logging
import os

import docker
import shcmd


logger = logging.getLogger(__name__)


class Paas(object):
    def __init__(self):
        self._docker = None
        self._user = None
        self._uid = None
        self._git = None
        self._construction_site = None
        self._rails_dependencies = None
        self._build_timeout = None
        self._git_deploy_key = None
        self._deb_mirror = None
        self._gem_mirror = None
        self._ruby_build_mirror = None
        self._docker_registry = None

    @property
    def docker_registry(self):
        return self._docker_registry

    @docker_registry.setter
    def docker_registry(self, new_registry):
        self._docker_registry = new_registry
        return self._docker_registry

    @property
    def docker(self):
        return self._docker

    @docker.setter
    def docker(self, docker_client):
        try:
            assert docker_client.ping()
        except:
            raise ValueError("can not talk to docker server")
        self._docker = docker_client
        return self._docker

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, new_user):
        self._user = new_user
        return self._user

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, new_uid):
        self._uid = new_uid
        return self._uid

    @property
    def git(self):
        return self._git

    @git.setter
    def git(self, new_git):
        self._git = new_git
        return self._git

    @property
    def construction_site(self):
        if self._construction_site is None:
            raise ValueError("you need to init paas first")
        return self._construction_site

    @construction_site.setter
    def construction_site(self, new_site):
        if os.path.isdir(new_site):
            abspath = os.path.realpath(new_site)
            if os.access(abspath, os.W_OK):
                self._construction_site = abspath
                logger.info("constrution site set to {0}".format(abspath))
                return
        raise ValueError("construction site dir should be writable")

    @property
    def rails_dependencies(self):
        return self._rails_dependencies[:]

    @rails_dependencies.setter
    def rails_dependencies(self, new_dep):
        self._rails_dependencies = new_dep[:]
        return self._rails_dependencies[:]

    @property
    def build_timeout(self):
        return self._build_timeout

    @build_timeout.setter
    def build_timeout(self, new_timeout):
        self._build_timeout = new_timeout
        return self._build_timeout

    @property
    def git_deploy_key(self):
        return self._git_deploy_key

    @git_deploy_key.setter
    def git_deploy_key(self, key_path):
        """**always set git first**"""
        try:
            shcmd.run(
                "ssh git@{0} -i {1} -o PasswordAuthentication=no".format(
                    self.git, key_path
                ),
                timeout=60
            )
        except:
            raise ValueError("can not talk to git server")
        self._git_deploy_key = open(key_path).read()
        return self._git_deploy_key

    @property
    def deb_mirror(self):
        return self._deb_mirror

    @deb_mirror.setter
    def deb_mirror(self, new_mirror):
        self._deb_mirror = new_mirror
        return self._deb_mirror

    @property
    def ruby_build_mirror(self):
        return self._ruby_build_mirror

    @ruby_build_mirror.setter
    def ruby_build_mirror(self, new_mirror):
        self._ruby_build_mirror = new_mirror
        return self._ruby_build_mirror

    @property
    def gem_mirror(self):
        return self._gem_mirror

    @gem_mirror.setter
    def gem_mirror(self, new_mirror):
        self._gem_mirror = new_mirror
        return self._gem_mirror

    def init_app(self, app):
        self.docker = docker.Client(**app.config["DOCKER_OPT"])
        self.user = app.config["PAAS_USER"]
        self.uid = app.config["PAAS_USER_UID"]
        self.construction_site = app.config["CONSTRUCTION_SITE"]
        self.rails_dependencies = app.config["RAILS_DEPENDENCIES"]
        self.build_timeout = app.config["BUILD_TIMEOUT"]
        self.git = app.config["GIT"]
        self.git_deploy_key = app.config["GIT_DEPLOY_KEY_PATH"]
        self.deb_mirror = app.config["DEB_MIRROR"]
        self.ruby_build_mirror = app.config["RUBY_BUILD_MIRROR"]
        self.gem_mirror = app.config["GEM_MIRROR"]
        self.docker_registry = app.config["DOCKER_REGISTRY"]


paas = Paas()
