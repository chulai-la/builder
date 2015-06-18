import json
import logging
import os
import traceback

import docker
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

    @property
    def construction_site(self):
        site = os.path.join(paas.construction_site, self.app.name)
        shcmd.mkdir(site)
        return site

    @property
    def exists(self):
        tags = {
            tag
            for image in paas.docker.images(name=self.app.tag_name)
            for tag in image["RepoTags"]
        }
        return self.tag in tags

    def build(self):
        omg = OutputManager()

        with shcmd.cd(self.construction_site):
            shcmd.rm(consts.BUILD_FAILURE_LOG)
            try:
                yield from omg.new_log(self.before_build())

                if self.exists:
                    yield from omg.new_log("image found, skip building...")
                else:
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
                yield from omg.new_log(self.after_build())
                yield from omg.new_event(build="success")
            except BaseException as exc:
                yield from omg.new_event(build="failed", reason=str(exc))
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

    def run_in_docker(self, command, volume):
        binds={
            on_host: dict(bind=in_docker, ro=False)
            for in_docker, on_host in volume.items()
        }
        binds.update({
            "/etc/localtime": dict(bind="/etc/localtime", ro=True)
        })
        cid = None
        name = "{0}-operation".format(self.app.name)
        try:
            res = paas.docker.create_container(
                self.tag,
                user=paas.user,
                command=command,
                mem_limit=0, # no limit of memory
                environment=self.app.env,
                volumes=list(volume.keys()),
                name=name,
                labels=[name],
                working_dir=self.app.work_dir,
                host_config=docker.utils.create_host_config(binds=binds)
            )
            cid = res["Id"]
            paas.docker.start(cid)

            for log in paas.docker.logs(cid, stream=True):
                yield log.decode("utf8").strip()

            retcode = paas.docker.inspect_container(cid)["State"]["ExitCode"]
            if retcode != 0:
                tip = "command [{0}] returned {1}, deleting container {2}"\
                    .format(command, retcode, cid)
                logger.error(tip)
                raise ChulaiBuildError(tip)
        finally:
            if cid is None:
                # if cid is none, check again using label
                containers = paas.docker.containers(
                    all=True,
                    filters=dict(label=name)
                )
                if containers:
                    cid = containers[0]["Id"]
            if cid is not None:
                paas.docker.remove_container(cid)

    def __str__(self):
        return "<Build {0} of {1}>".format(self.commit, self.app.name)

class RailsBuild(Build):
    @property
    def need_bundling(self):
        result = True
        if self.fresh_build:
            logger.info("fresh build, need bundling")
        elif "Gemfile.lock" in self.diff:
            logger.info("Gemfile.lock has changed, need bundling")
        elif "Gemfile" in self.diff:
            logger.info("Gemfile has changed, need bundling")
        else:
            logger.info("skip bundling")
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

        dbconfig = env.get_template("rails/dbconfig").render(
            build=self
        )

        tar = shcmd.tar.TarGenerator()
        tar.add_fileobj("Dockerfile", dockerfile)
        tar.add_fileobj("id_rsa", paas.git_deploy_key)
        tar.add_fileobj("Gemfile", gf.gemfile)
        tar.add_fileobj("Gemfile.lock", gf.gemfile_lock)
        tar.add_fileobj("database.yml", dbconfig)
        return tar.tar_io

    @property
    def need_precompilation(self):
        assets_files = set()
        for file_changed in self.diff:
            if file_changed.startswith("vendor/assets"):
                assets_files.add(file_changed)
            elif file_changed.startswith("app/assets"):
                assets_files.add(file_changed)
        if assets_files:
            logger.debug("following assets file has changed:\n{0}".format(
                ", ".join(assets_files)
            ))
            logger.info("need precompile")
            return True
        else:
            return False

    @property
    def need_migration(self):
        migrate_flag = "db/schema.rb" in self.diff
        if migrate_flag:
            logger.info("need migration")
        return migrate_flag

    def migrate(self):
        yield "going to migrate..."
        cmd = (
            "bundle exec"
            " rake db:migrate"
            " RAILS_ENV=production"
        )
        yield from self.run_in_docker(cmd, {})

    def precompile(self):
        yield "going to precomile..."
        cmd = (
            "bundle exec "
            " rake assets:precompile"
            " RAILS_ENV=production"
            " RAILS_GROUP=assets"
        )
        shcmd.rm(self.host_precompilation_site, isdir=True)
        volumes = {
            os.path.join(self.app.work_dir, "public", "assets"):
            self.host_precompilation_site
        }
        yield from self.run_in_docker(cmd, volumes)

    @property
    def host_precompilation_site(self):
        site = os.path.join(self.construction_site, "assets")
        shcmd.mkdir(site)
        return site

    def after_build(self):
        if self.need_precompilation:
            yield from self.precompile()
        if self.need_migration:
            yield from self.migrate()
        yield from super(RailsBuild, self).after_build()
