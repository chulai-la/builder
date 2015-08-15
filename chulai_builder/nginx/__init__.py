from flask import Blueprint
from flask import current_app
from flask import request
from flask import jsonify


from .app_nginx import AppNginx

api = Blueprint("nginx_api", __name__)


@api.route("/router/<app_id>", methods=["PUT"])
def update_router(app_id):
    try:
        nginx = AppNginx(
            app_id,
            request.json["auth-token"],
            request.json["domains"],
            request.json["instances"],
            request.json["client-max-size-in-mb"],
            request.json["timeout-in-s"],
            request.json["sleeping-enabled"],
            request.json["streaming-enabled"]
        )
    except KeyError as exc:
        current_app.logger.error("invalid request", exc_info=True)
        return jsonify(
            status="error",
            message="missing key [{0}]".format(exc)
        )
    nginx.publish()
    return jsonify(status="success", message="blancer updated")


@api.route("/router/<app_id>", methods=["DELETE"])
def destroy_router(app_id):
    nginx = AppNginx(
        app_id,
        auth_token=None,
        domains=None,
        instances=None,
        client_max_size=None,
        timeout=None,
        sleeping_enabled=None,
        streaming_enabled=None
    )
    nginx.destroy()
    return jsonify(status="success", message="blancer updated")
