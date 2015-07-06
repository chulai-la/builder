# -*- coding: utf8 -*-

import os
import sys

import flask.ext.script
import jinja2
import shcmd


from chulai_builder import create_app, paas

__curdir__ = os.path.realpath(os.path.dirname(__file__))

app = create_app(os.path.join(__curdir__, "config.cfg"))
manager = flask.ext.script.Manager(app)


@manager.command
def build(env):
    ENVS = dict(
        base="14.04.2",
        node="0.12.6",
        ruby="2.2.2"
    )
    with shcmd.cd(os.path.join(__curdir__, "images")):
        template = jinja2.Template(open("{0}.dockerfile".format(env)).read())
        dockerfile = template.render(paas=paas)
        try:
            with open("Dockerfile", "wt") as df:
                df.write(dockerfile)
            res = paas.docker.build(
                ".",
                rm=True,
                nocache=True,
                tag="{0}/{1}:{2}".format(paas.docker_registry, env, ENVS[env])
            )
            for line in res:
                print(line)
        finally:
            shcmd.rm("Dockerfile")
    print(env, paas)


@manager.command
def test():
    import nose
    with app.app_context():
        nose.run(argv=list(sys.argv) + ["tests"])


if __name__ == "__main__":
    manager.run()
