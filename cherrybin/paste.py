"""Blueprint handling paste operations"""

import datetime
from flask import Blueprint, request, redirect, url_for, g, render_template
from google.cloud.firestore_v1.base_query import FieldFilter
from cherrybin.pyrebase import firebase_db
from cherrybin.auth import login_required
from cherrybin.sqids import sqids
from cherrybin.crypto import encrypt_paste, decrypt_paste, decrypt
from cherrybin.firebase_admin import firestore_db

bp = Blueprint("paste", __name__, url_prefix="/paste")
pastes_ref = firestore_db.collection("pastes")


class Paste:
    def __init__(self, user_id, created_at, title, contents, paste_id=None):
        self.user_id = user_id
        self.created_at = created_at
        self.title = title
        self.contents = contents
        self.paste_id = paste_id

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "created_at": self.created_at,
            "title": self.title,
            "contents": self.contents,
            "paste_id": self.paste_id,
        }


@bp.post("/create")
def create():
    """Uploads paste to database"""

    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    paste_id = sqids.encode([int(timestamp.timestamp())])
    user_id = 0

    if g.user is not None:
        user_id = g.user["localId"]

    title = "Unnamed"

    if request.form["pasteName"]:
        title = request.form["pasteName"]

    title_enc, contents_enc = encrypt_paste(title, request.form["pasteText"])

    pastes_ref.document(paste_id).set(
        Paste(
            user_id,
            timestamp,
            title_enc,
            contents_enc,
        ).to_dict()
    )

    return redirect(url_for("paste.get", paste_id=paste_id))


@bp.get("/my")
@login_required
def my_pastes():
    """Get a list of current user's pastes"""

    user_id = g.user["localId"]

    pastes = (
        pastes_ref.where(filter=FieldFilter("user_id", "==", user_id))
        .select(["title", "created_at", "user_id"])
        .stream()
    )

    paste_list = []

    for paste in pastes:
        paste_tmp = paste.to_dict()
        paste_tmp["paste_id"] = paste.id
        print(paste.id)
        paste_tmp["title"] = decrypt(paste_tmp["title"])
        paste_list.append(paste_tmp)

    return render_template("pastes/my.jinja", pastes=paste_list)


@bp.get("/get/<string:paste_id>")
def get(paste_id):
    """Get the paste by its id"""

    # paste = firebase_db.child("paste_meta").child(paste_id).get(token).val()
    # paste_contents = (
    #     firebase_db.child("paste_contents").child(paste_id).get(token)
    # ).val()

    # paste.update(paste_contents)

    paste = pastes_ref.document(paste_id).get()

    if paste.exists:
        paste = paste.to_dict()
        paste["title"], paste["contents"] = decrypt_paste(
            paste["title"], paste["contents"]
        )
        return render_template("pastes/view.jinja", paste=paste)
    else:
        # TODO: Throw 404
        print("404")
