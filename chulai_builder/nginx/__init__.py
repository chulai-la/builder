from flask import Blueprint, Response
from flask import request
from flask import g
from flask import abort


from .app_nginx import AppNginx

api = Blueprint("nginx_api", __name__)


@api.before_request
def setup_nginx():
    try:
        g.nginx = AppNginx(
            request.json["app-id"],
            request.json["auth-token"],
            request.json["domains"],
            request.json["instances"],
            request.json["client-max-size-in-mb"],
            request.json["timeout-in-s"],
            request.json["sleeping-enabled"],
            request.json["streaming-enabled"]
        )
    except KeyError as exc:
        abort(400)


@api.route("/router/update", methods=["PUT"])
def update_router():
    g.nginx