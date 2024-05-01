"""Blueprint handling pasta operations"""

import time
from base64 import b64encode, b64decode
from flask import Blueprint, request, redirect, url_for, g, render_template, session
from instapasta.pyrebase import firebase_db
from instapasta.auth import login_required
from instapasta.sqids import sqids
from .pyrebase import firebase_auth

bp = Blueprint("pasta", __name__, url_prefix="/pasta")


@bp.post("/create")
# @login_required
def create():
    """Uploads pasta to database"""

    if g.user is None:
        session["user"] = g.user = firebase_auth.sign_in_anonymous()

    timestamp = time.time()
    pasta_id = sqids.encode([int(timestamp)])

    pasta_meta = {
        "name": request.form["pastaName"] if request.form["pastaName"] else "Unnamed",
        "user_id": g.user["localId"],
        "created_at": timestamp,
    }

    pasta_contents = {"contents": request.form["pastaText"]}

    firebase_db.child("pasta_meta").child(pasta_id).set(pasta_meta, g.user["idToken"])
    firebase_db.child("pasta_contents").child(pasta_id).set(
        pasta_contents, g.user["idToken"]
    )

    return redirect(url_for("pasta.get", pasta_id=pasta_id))


@bp.get("/my")
@login_required
def my_pastas():
    """Get a list of current user's pastas"""

    user_id = g.user["localId"]

    pasta_response = (
        firebase_db.child("pasta_meta")
        .order_by_child("user_id")
        .equal_to(user_id)
        .get(g.user["idToken"])
    )

    return render_template("pastas/my.jinja", pastas=pasta_response.val())


@bp.get("/get/<string:pasta_id>")
@login_required
def get(pasta_id):
    """Get the pasta by its id"""

    pasta = firebase_db.child("pasta_meta").child(pasta_id).get(g.user["idToken"]).val()
    pasta_contents = (
        firebase_db.child("pasta_contents").child(pasta_id).get(g.user["idToken"])
    ).val()

    pasta.update(pasta_contents)

    return render_template("pastas/view.jinja", pasta=pasta)
