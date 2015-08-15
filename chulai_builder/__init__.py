from flask import Flask
from .paas import paas


def create_app(config_path):
    app = Flask(__name__)
    app.config.from_pyfile(config_path)

    paas.init_app(app)

    from . import builders
    app.register_blueprint(builders.api)

    from . import nginx
    app.register_blueprint(nginx.api)

    return app
