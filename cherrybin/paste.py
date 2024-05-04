"""Blueprint handling paste operations"""

import datetime
from dataclasses import dataclass
from flask import Blueprint, request, redirect, url_for, g, render_template
from google.cloud.firestore_v1.base_query import FieldFilter
from cherrybin.sqids import sqids
from cherrybin.crypto import encrypt, decrypt
from cherrybin.firebase_admin import firestore_db

bp = Blueprint("paste", __name__, url_prefix="/paste")
pastes_ref = firestore_db.collection("pastes")


@dataclass
class PasteMeta:
    """
    Utility fields of a Paste.
    """

    user_id: str
    created_at: datetime.datetime


class Paste:
    """
    Class representing the Paste object.
    """

    def __init__(self, meta: PasteMeta, title, contents=None, to_encrypt=False):
        self.meta = meta
        self.title = encrypt(title) if to_encrypt else title
        self.contents = encrypt(contents) if to_encrypt else contents

    def to_dict(self, to_decrypt=False):
        """Return Paste as a dictionary.

        Args:
           to_decrypt: Flag signaling wether to decrypt encrypted fields (optional).
        """

        return {
            "user_id": self.meta.user_id,
            "created_at": self.meta.created_at,
            "title": decrypt(self.title) if to_decrypt else self.title,
            "contents": (
                decrypt(self.contents)
                if to_decrypt and self.contents
                else self.contents
            ),
        }

    @staticmethod
    def from_dict(source, encrypted):
        """Reconstruct Paste from the dictionary.

        Args:
           encrypted: Flag signaling wether the dictionary contains encrypted fields.
        """

        user_id = source.get("user_id")
        created_at = source.get("created_at")
        title = decrypt(source.get("title")) if encrypted else source.get("title")
        contents = (
            decrypt(source.get("contents"))
            if encrypted
            else source.get("contents", None)
        )
        return Paste(
            PasteMeta(user_id, created_at),
            title,
            contents,
        )


@bp.post("/create")
def create():
    """Uploads paste to database"""

    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    paste_id = sqids.encode([int(timestamp.timestamp())])
    user_id = 0

    if g.user is not None:
        user_id = g.user["localId"]

    pastes_ref.document(paste_id).set(
        Paste(
            PasteMeta(user_id, timestamp),
            request.form["pasteName"] if request.form["pasteName"] else "Unnamed",
            request.form["pasteText"],
            to_encrypt=True,
        ).to_dict()
    )

    return redirect(url_for("paste.get", paste_id=paste_id))


@bp.get("/<string:user_id>")
def user(user_id):
    """Get a list of given user's pastes"""

    pastes = __get_user_pastes(user_id)

    paste_list = []

    for paste in pastes:
        paste_tmp = paste.to_dict()
        paste_tmp["paste_id"] = paste.id
        paste_tmp["title"] = decrypt(paste_tmp["title"])
        paste_list.append(paste_tmp)

    return render_template("pastes/my.jinja", pastes=paste_list)


@bp.get("/get/<string:paste_id>")
def get(paste_id):
    """Get the paste by its id"""

    paste = pastes_ref.document(paste_id).get()

    if paste.exists:
        paste = Paste.from_dict(paste.to_dict(), encrypted=True)
        return render_template("pastes/view.jinja", paste=paste)

    return render_template("home.jinja")


def __get_user_pastes(user_id):
    return (
        pastes_ref.where(filter=FieldFilter("user_id", "==", user_id))
        .select(["title", "created_at", "user_id"])
        .stream()
    )
