import json
import os

from ..paas import paas

from .env import env


class Instance(object):
    def __init__(self, build, instance_id, instance_type, port):
        self._build = build
        self._instance_id = instance_id
        self._instance_type = instance_type
        self._port = port

    @property
    def build(self):
        return self._build

    @property
    def start_sec(self):
        return self.build.app.env.get("START_TIMEOUT", paas.start_timeout)

    @property
    def stop_sec(self):
        return self.build.app.env.get("STOP_TIMEOUT", paas.start_timeout)

    @property
    def dirs_to_make(self):
        return [self.logs_dir, self.stdlogs_dir]

    @property
    def instance_id(self):
        return self._instance_id

    @property
    def port(self):
        return self._port

    @property
    def instance_type(self):
        return self._instance_type

    @property
    def supervisor_conf(self):
        template = env.get_template(
            "supervisor.conf".format(self.instance_type)
        )
        return template.render(instance=self, paas=paas)

    @property
    def playground(self):
        return os.path.join(paas.playground, self.instance_id)

    @property
    def env_json(self):
        return json.dumps(self.build.app.env)

    @property
    def env(self):
        return self.build.app.env.copy()

    @property
    def logs_dir(self):
        return os.path.join(self.playground, "chulai-log.d")

    @property
    def stdlogs_dir(self):
        return os.path.join(self.playground, "stdout-log.d")
