import os
from dotenv import load_dotenv
from flask import Flask, render_template
from .asset import Asset
from . import auth

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = FLASK_SECRET_KEY
    Asset(app)

    app.register_blueprint(auth.bp)

    @app.route("/")
    def index():
        return render_template("base.html")

    return app
