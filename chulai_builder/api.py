from flask import Blueprint
from flask import request


builder_api = Blueprint("builder_api", __name__)


App = None


@builder_api.route()
def build():
    app = App(
        request.json["app_name"],
        "rails",  # app_type
        request.json["repo"],
        "ruby:2.2.0",  # base image
        request.json["current_image"] or None,
        dict(secret="secret"),
    )

    build = app.new_build(request.json["commmit"])

    for line in build.build():
        print(line)
