"""Blueprint handling pasta operations"""

import time
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

    timestamp = time.time()
    pasta_id = sqids.encode([int(timestamp)])
    user_id = 0
    token = None

    if g.user is not None:
        user_id = g.user["localId"]
        token = g.user["idToken"]

    pasta_meta = {
        "name": request.form["pastaName"] if request.form["pastaName"] else "Unnamed",
        "user_id": user_id,
        "created_at": timestamp,
    }

    pasta_contents = {"contents": request.form["pastaText"]}

    firebase_db.child("pasta_meta").child(pasta_id).set(pasta_meta, token)
    firebase_db.child("pasta_contents").child(pasta_id).set(pasta_contents, token)

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
# @login_required
def get(pasta_id):
    """Get the pasta by its id"""

    token = None

    # TODO: Refactor this into separate method (maybe)
    if g.user is not None:
        token = g.user["idToken"]

    pasta = firebase_db.child("pasta_meta").child(pasta_id).get(token).val()
    pasta_contents = (
        firebase_db.child("pasta_contents").child(pasta_id).get(token)
    ).val()

    pasta.update(pasta_contents)

    return render_template("pastas/view.jinja", pasta=pasta)
