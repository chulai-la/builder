from flask import Blueprint, Response
from flask import request
from flask import g
from flask import abort

from .builders import App

builder_api = Blueprint("builder_api", __name__)


@builder_api.before_request
def setup_build():
    try:
        app = App(
            request.json["app-id"],
            "rails",  # app_type
            request.json["repo"],
            "ruby:2.2.0",  # base image
            request.json["current-image"],
            request.json["env"]
        )
    except:
        abort(400)
    g.build = app.get_build(request.json["commit"])


@builder_api.route("/builds", methods=["POST"])
def build():
    return Response(g.build.build(), mimetype="application/x-chulai-log")


@builder_api.route("/supervisor", methods=["POST"])
def gen_supervisor_conf():
    try:
        instance = g.build.get_instance(
            request.json["instance-id"],
            request.json["instance-type"],
            request.json.get("port")
        )
    except:
        abort(400)
    return instance.supervisor_conf
