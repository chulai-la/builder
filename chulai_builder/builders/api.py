import json

from flask import Blueprint, Response
from flask import current_app
from flask import g
from flask import request

from .app import App


builder_api = Blueprint("builder_api", __name__)


@builder_api.before_request
def setup_build():
    try:
        app = App(
            request.json["app-id"],
            request.json["app-type"],
            request.json["repo"],
            request.json["base-image"],
            request.json["current-image"],
            request.json["environments"]
        )
        commit = request.json["commit"]
    except KeyError as exc:
        tip = "missing field: {0}".format(exc)
        current_app.logger.error(tip, exc_info=True)
        return Response(
            json.dumps(dict(status="error", tip=tip)),
            status=400,
            mimetype="application/json"
        )
    g.build = app.get_build(commit)


@builder_api.route("/builds", methods=["POST"])
def build():
    return Response(g.build.build(), mimetype="application/x-chulai-log")
