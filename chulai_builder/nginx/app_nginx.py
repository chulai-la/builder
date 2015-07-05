import os

import shcmd

from ..paas import paas

from .env import env


class AppNginx(object):
    def __init__(
        self,
        app_id,
        auth_token,
        domains,
        instances,
        client_max_size,
        timeout,
        sleeping_enabled,
        streaming_enabled
    ):
        self._app_id = app_id
        self._auth_token = auth_token
        self._domains = domains
        self._instances = instances
        self._client_max_size = client_max_size
        self._timeout = timeout
        self._sleeping_enabled = sleeping_enabled
        self._streaming_enabled = streaming_enabled

    @property
    def app_id(self):
        return self._app_id

    @property
    def auth_token(self):
        return self._auth_token

    @property
    def domains(self):
        return self._domains[:]

    @property
    def instances(self):
        return self._instances.copy()

    @property
    def client_max_size(self):
        return self._client_max_size

    @property
    def timeout(self):
        return self._timeout

    @property
    def sleeping_enabled(self):
        return self._sleeping_enabled

    @property
    def streaming_enabled(self):
        return self._streaming_enabled

    @property
    def assets_dir(self):
        return os.path.join(paas.assets_dir, self.app_id)

    @property
    def nginx_conf(self):
        template = env.get_template("nginx.conf")
        return template.render(app=self, paas=paas)

    @property
    def nginx_conf_path(self):
        return os.path.join(
            paas.nginx_conf_dir,
            "{0}.ini".format(self.app_id)
        )

    def publish(self):
        with open(self.nginx_conf_path, "wt") as conf_f:
            conf_f.write(self.nginx_conf)
        shcmd.run("sudo /etc/init.d/nginx configtest")
        shcmd.run("sudo /etc/init.d/nginx reload")
