from flask import Flask

from app.routes import api_bp, admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    return app
