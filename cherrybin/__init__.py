import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session
from cherrybin import auth, paste
from cherrybin.crypto import encrypt_paste
import cherrybin.firebase_admin
from cherrybin.paste import construct_expiry_values
from .asset import Asset

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = FLASK_SECRET_KEY
    Asset(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(paste.bp)

    @app.template_filter()
    def format_time(value):
        return value.strftime("%d.%m.%Y %H:%m")

    @app.route("/")
    def index():
        return render_template(
            "home.jinja", expiry_options=construct_expiry_values()
        )  # TODO: Disallow anonymous user to create paste with no expiration

    encrypt_paste("title", "contents")

    return app
