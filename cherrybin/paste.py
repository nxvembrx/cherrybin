"""Blueprint handling paste operations"""

import time
from flask import Blueprint, request, redirect, url_for, g, render_template, session
from cherrybin.pyrebase import firebase_db
from cherrybin.auth import login_required
from cherrybin.sqids import sqids
from cherrybin.crypto import encrypt_paste, decrypt_paste, decrypt
from .pyrebase import firebase_auth

bp = Blueprint("paste", __name__, url_prefix="/paste")


@bp.post("/create")
# @login_required
def create():
    """Uploads paste to database"""

    timestamp = time.time()
    paste_id = sqids.encode([int(timestamp)])
    user_id = 0
    token = None

    if g.user is not None:
        user_id = g.user["localId"]
        token = g.user["idToken"]

    name = "Unnamed"

    if request.form["pasteName"]:
        name = request.form["pasteName"]

    name_enc, contents_enc = encrypt_paste(name, request.form["pasteText"])

    paste_meta = {
        "name": name_enc,
        "user_id": user_id,
        "created_at": timestamp,
    }

    paste_contents = {"contents": contents_enc}

    firebase_db.child("paste_meta").child(paste_id).set(paste_meta, token)
    firebase_db.child("paste_contents").child(paste_id).set(paste_contents, token)

    return redirect(url_for("paste.get", paste_id=paste_id))


@bp.get("/my")
@login_required
def my_pastes():
    """Get a list of current user's pastes"""

    user_id = g.user["localId"]

    paste_response = (
        firebase_db.child("paste_meta")
        .order_by_child("user_id")
        .equal_to(user_id)
        .get(g.user["idToken"])
    )
    paste_list = paste_response.val()

    for _, paste in paste_list.items():
        paste["name"] = decrypt(paste["name"])

    return render_template("pastes/my.jinja", pastes=paste_list)


@bp.get("/get/<string:paste_id>")
# @login_required
def get(paste_id):
    """Get the paste by its id"""

    token = None

    # TODO: Refactor this into separate method (maybe)
    if g.user is not None:
        token = g.user["idToken"]

    paste = firebase_db.child("paste_meta").child(paste_id).get(token).val()
    paste_contents = (
        firebase_db.child("paste_contents").child(paste_id).get(token)
    ).val()

    paste.update(paste_contents)

    paste["name"], paste["contents"] = decrypt_paste(paste["name"], paste["contents"])

    return render_template("pastes/view.jinja", paste=paste)
