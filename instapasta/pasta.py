"""Blueprint handling pasta operations"""

import time
from flask import Blueprint, request, redirect, url_for, g, render_template, session
from instapasta.pyrebase import firebase_db
from instapasta.auth import login_required
from instapasta.sqids import sqids
from instapasta.crypto import encrypt_pasta, decrypt_pasta, decrypt
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

    name = "Unnamed"

    if request.form["pastaName"]:
        name = request.form["pastaName"]

    name_enc, contents_enc = encrypt_pasta(name, request.form["pastaText"])

    pasta_meta = {
        "name": name_enc,
        "user_id": user_id,
        "created_at": timestamp,
    }

    pasta_contents = {"contents": contents_enc}

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
    pasta_list = pasta_response.val()

    for _, pasta in pasta_list.items():
        pasta["name"] = decrypt(pasta["name"])

    return render_template("pastas/my.jinja", pastas=pasta_list)


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

    pasta["name"], pasta["contents"] = decrypt_pasta(pasta["name"], pasta["contents"])

    return render_template("pastas/view.jinja", pasta=pasta)
