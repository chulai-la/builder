from flask import Flask
from .builders.paas import paas


def create_app(config_path):
    app = Flask(__name__)
    app.config.from_pyfile(config_path)

    paas.init_app(app)

    from .api import builder_api
    app.register_blueprint(builder_api)

    return app
