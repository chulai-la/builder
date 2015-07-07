from flask import Blueprint, Response
from flask import abort
from flask import current_app
from flask import g
from flask import jsonify
from flask import request

import requests

from .builders import App
from .paas import paas

builder_api = Blueprint("builder_api", __name__)


@builder_api.before_request
def setup_build():
    try:
        app = App(
            request.json["app-id"],
            "rails",  # app_type
            request.json["repo"],
            request.json["base-image"],
            request.json["current-image"],
            request.json["env"]
        )
    except KeyError:
        current_app.logger.error("missing fields", exc_info=True)
        abort(400)
    g.build = app.get_build(request.json["commit"])


@builder_api.route("/builds", methods=["POST"])
def build():
    return Response(g.build.build(), mimetype="application/x-chulai-log")


@builder_api.route("/instances/<instance_id>/init", methods=["POST"])
def gen_supervisor_conf(instance_id):
    try:
        instance = g.build.get_instance(
            request.json["instance-id"],
            request.json["instance-type"],
            request.json.get("port")
        )
    except KeyError:
        current_app.logger.error("missing fields", exc_info=True)
        abort(400)
    res = requests.put(
        "http://{0}/instances/deploy".format(paas.agent_host),
        json={
            "supervisor-config": instance.supervisor_conf,
            "files-to-mount": {},  # FIXME
            "dirs-to-make": []
        }
    )
    res.raise_for_status()
    return jsonify(status="success")
