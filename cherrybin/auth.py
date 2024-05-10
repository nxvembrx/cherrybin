"""Blueprint handling authentication and authorization"""

import json
import time
import functools
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    flash,
    session,
    g,
)
from requests.exceptions import HTTPError
from .pyrebase import firebase_auth

FIREBASE_EXPIRES_IN_SECONDS = 3600

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/signup", methods=("GET", "POST"))
def signup():
    """Creates user record in the database and redirects to login if successful"""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = None

        if not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"

        if error is None:
            try:
                firebase_auth.create_user_with_email_and_password(email, password)
            except Exception as e:
                print(e)
                error = e
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/signup.jinja")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Logs user in, redirects home if successful"""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = None

        try:
            user = firebase_auth.sign_in_with_email_and_password(email, password)
        except Exception as e:
            error = e
        else:
            session.clear()
            session["user"] = user
            update_signed_in_at()
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.jinja")


@bp.before_app_request
def load_logged_in_user():
    """Fetches the current user from the session and sets it in the g namespace"""

    user = session.get("user")

    if user is None:
        g.user = None
    else:
        if is_token_expired() >= FIREBASE_EXPIRES_IN_SECONDS:
            try:
                fresh_token = firebase_auth.refresh(user["refreshToken"])["idToken"]
                session["user"]["idToken"] = fresh_token
                g.user = session["user"]
                update_signed_in_at()
            except HTTPError as e:
                session.clear()
                error = json.loads(e.strerror)["error"]["message"]
                flash(error)

        g.user = user


@bp.route("/logout")
def logout():
    """Clears the session for the user"""

    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """Checks if user is present in the g namespace, otherwise redirects to login"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def is_token_expired():
    return int(time.time()) - session.get("signed_in_at")


def update_signed_in_at():
    session["signed_in_at"] = int(time.time())


@bp.route("/user/<string:user_id>", methods=("GET", "POST"))
def profile(user_id):

    user = session.get("user")

    error = None

    if user["localId"] != user_id:
        error = "Unauthorized"
        flash(error)
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        token = user["idToken"]
        firebase_auth.update_profile(token, request.form["userDisplayName"])
        new_name = firebase_auth.get_account_info(token)["users"][0]["displayName"]
        user["displayName"] = new_name
        session["user"] = user

    return render_template("auth/profile.jinja")
