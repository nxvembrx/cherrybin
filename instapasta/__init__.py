import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session
from .asset import Asset
from . import auth, pasta

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = FLASK_SECRET_KEY
    Asset(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(pasta.bp)

    @app.template_filter()
    def format_time(value):
        return datetime.fromtimestamp(value).strftime("%d.%m.%Y %H:%m")

    @app.route("/")
    def index():
        return render_template("home.jinja")

    return app
