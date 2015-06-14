import json
import logging
import os
import traceback

import shcmd

from . import consts
from .paas import paas
from .errors import ChulaiBuildError
from .gem import Gemfile
from .template import env
from .utils import OutputManager


logger = logging.getLogger(__name__)


class Build(object):
    def __init__(self, app, commit):
        """
        :param current: current build's commit
        :param commit: commit-id want to build
        """
        self._app = app
        self._commit = commit

    @property
    def app(self):
        return self._app

    @property
    def fresh_build(self):
        return self.app.current is None

    @property
    def commit(self):
        return self._commit

    @property
    def tag(self):
        return "{0}:{1}".format(self.app.tag_name, self.commit)

    @property
    def diff(self):
        if self._diff is None:
            raise ChulaiBuildError(
                "you must analyze before you can check the diff"
            )
        return self._diff

    @property
    def tracked(self):
        if self._tracked is None:
            raise ChulaiBuildError(
                "you must analyze before you can check the tracked"
            )
        return self._tracked

    @property
    def extra_deps(self):
        return ["zlib1g-dev"]

    def sync_codebase(self):
        repo = self.app.repo
        if os.path.isdir(consts.LOCAL_GIT):
            with shcmd.cd(consts.LOCAL_GIT):
                yield "fetching..."
                logger.info("fetching code from {0}".format(repo))
                shcmd.run("git reset --hard")
                shcmd.run("git clean -fdx")
                shcmd.run("git remote set-url origin {0}".format(repo))
                shcmd.run("git fetch origin")
        else:
            yield "cloning..."
            logger.info("cloning code from {0}".format(repo))
            shcmd.rm(consts.LOCAL_GIT, isdir=True)
            shcmd.run("git clone {0} {1}".format(repo, consts.LOCAL_GIT))

    def analyze(self):
        with shcmd.cd(consts.LOCAL_GIT):
            shcmd.run("git checkout {0}".format(self.commit))
            self._tracked = set(
                fname
                for fname in shcmd.run("git ls-files").stdout.splitlines()
            )
            if self.app.current is None:
                self._diff = self._tracked
            else:
                cmd = "git diff {0} {1} --name-only".format(
                    self.app.current, self.commit
                )
                self._diff = set(shcmd.run(cmd).stdout.splitlines())

    @property
    def preflight_report(self):
        template = env.get_template("rails/preflight_report")
        return template.render(build=self)

    @property
    def final_report(self):
        return "final report"

    def before_build(self):
        # before build
        yield "analyzing..."
        yield from self.sync_codebase()
        self.analyze()
        yield self.preflight_report

    def prepare_context(self):
        raise NotImplementedError("prepare context not implemented")

    def build(self):
        site = os.path.join(paas.construction_site, self.app.name)
        omg = OutputManager()

        with shcmd.cd(site, create=True):
            shcmd.rm(consts.BUILD_FAILURE_LOG)
            try:
                yield from omg.new_log(self.before_build())

                for line in paas.docker.build(
                    fileobj=self.prepare_context(),
                    rm=True,
                    forcerm=True,
                    tag=self.tag,
                    nocache=True,
                    timeout=paas.build_timeout,
                    custom_context=True
                ):
                    output = json.loads(line.decode("utf8"))
                    if "error" in output:
                        raise ChulaiBuildError(output["error"])
                    elif "stream" in output:
                        yield from omg.new_log(output["stream"])
                    else:
                        raise ValueError(
                            "unknown docker build error: {0}".format(output)
                        )
                # after build
                # yield from self.after_build()
                yield from omg.new_event(build="success")
            except:
                yield from omg.new_event(build="failed")
                logger.error("build error", exc_info=True)
                with open(consts.BUILD_FAILURE_LOG, "wt") as log_f:
                    log_f.write("trace:\n{0}\noutput:\n{1}\n".format(
                        traceback.format_exc(), omg.log
                    ))

    def after_build(self):
        yield self.final_report

    @property
    def ancestor(self):
        if self.fresh_build:
            return self.app.base_image
        else:
            return "{0}:{1}".format(self.app.tag_name, self.app.current)

    def __str__(self):
        return "<Build {0} of {1}>".format(self.commit, self.app.name)


class RailsBuild(Build):
    @property
    def need_bundling(self):
        result = True
        if self.fresh_build:
            logger.info("fresh build, need migration")
        elif "Gemfile.lock" in self.diff:
            logger.info("Gemfile.lock has changed, need migration")
        elif "Gemfile" in self.diff:
            logger.info("Gemfile has changed, need migration")
        else:
            logger.info("skip migration")
            result = False
        return result

    @shcmd.cd_to(consts.LOCAL_GIT)
    def prepare_context(self):
        # inject required gems (mysql and puma)
        gf = Gemfile(open("Gemfile").read(), open("Gemfile.lock").read())

        for deps in paas.rails_dependencies:
            gf.inject_dependency(*deps)

        # gererate dockerfile
        dockerfile = env.get_template("rails.dockerfile").render(
            build=self, paas=paas
        )

        tar = shcmd.tar.TarGenerator()
        tar.add_fileobj("Dockerfile", dockerfile)
        tar.add_fileobj("id_rsa", paas.git_deploy_key)
        tar.add_fileobj("Gemfile", gf.gemfile)
        tar.add_fileobj("Gemfile.lock", gf.gemfile_lock)
        return tar.tar_io
