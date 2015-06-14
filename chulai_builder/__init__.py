from flask import Flask


def create_app(config_path):
    app = Flask(__name__)
    app.config.from_pyfile(config_path)

    from .builders.paas import paas
    paas.init_app(app)

    return app
