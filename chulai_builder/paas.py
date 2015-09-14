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
        self._build_timeout = None
        self._git_deploy_key = None
        self._deb_mirror = None
        self._gem_mirror = None
        self._ruby_build_mirror = None
        self._docker_registry = None

        self._assets_dir = None
        self._admin_host = None
        self._nginx_path = None

    @property
    def nginx_path(self):
        return self._nginx_path

    @nginx_path.setter
    def nginx_path(self, nginx_path):
        if not os.path.isfile(nginx_path):
            raise ValueError("invalid nginx path")
        self._nginx_path = nginx_path
        return self._nginx_path

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
        self._construction_site = _can_write(new_site, "constrution site")
        return self._construction_site

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
                "ssh git@{0} -i {1}".format(
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

    @property
    def assets_dir(self):
        return self._assets_dir

    @assets_dir.setter
    def assets_dir(self, new_dir):
        self._assets_dir = _can_write(new_dir, "app assets dir")
        return self._assets_dir

    @property
    def admin_host(self):
        return self._admin_host

    @admin_host.setter
    def admin_host(self, new_host):
        self._admin_host = new_host
        return self._admin_host

    @property
    def nginx_conf_dir(self):
        return self._nginx_conf_dir

    @nginx_conf_dir.setter
    def nginx_conf_dir(self, conf_dir):
        self._nginx_conf_dir = _can_write(conf_dir, "nginx conf dir")
        return self._nginx_conf_dir

    def init_app(self, app):
        self.docker = docker.Client(**app.config["DOCKER_OPT"])
        self.user = app.config["PAAS_USER"]
        self.uid = app.config["PAAS_USER_UID"]
        self.construction_site = app.config["CONSTRUCTION_SITE"]
        self.build_timeout = app.config["BUILD_TIMEOUT"]
        self.git = app.config["GIT"]
        self.git_deploy_key = app.config["GIT_DEPLOY_KEY_PATH"]
        self.deb_mirror = app.config["DEB_MIRROR"]
        self.ruby_build_mirror = app.config["RUBY_BUILD_MIRROR"]
        self.gem_mirror = app.config["GEM_MIRROR"]
        self.docker_registry = app.config["DOCKER_REGISTRY"]
        self.assets_dir = app.config["ASSETS_DIR"]
        self.admin_host = app.config["ADMIN_HOST"]
        self.nginx_conf_dir = app.config["NGINX_CONF_DIR"]
        self.nginx_path = app.config["NGINX_PATH"]


def _can_write(test_path, path_name):
    if os.path.isdir(test_path):
        abspath = os.path.realpath(test_path)
        if os.access(abspath, os.W_OK):
            logger.info("{0} set to [{1}]".format(path_name, abspath))
            return abspath
    raise ValueError("{0} dir should be writable".format(path_name))


paas = Paas()
