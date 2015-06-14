from flask import Blueprint, Response
from flask import request

from .builders import App

builder_api = Blueprint("builder_api", __name__)


@builder_api.route("/builds", methods=["POST"])
def build():
    app = App(
        request.json["app-id"],
        "rails",  # app_type
        request.json["repo"],
        "ruby:2.2.0",  # base image
        request.json["current-image"],
        {}
    )

    build = app.new_build(request.json["commit"])

    return Response(build.build(), mimetype="application/x-chulai-log")
