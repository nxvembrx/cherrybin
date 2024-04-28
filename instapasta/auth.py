"""Blueprint handling authentication and authorization"""

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
from .pyrebase import firebase_auth


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
