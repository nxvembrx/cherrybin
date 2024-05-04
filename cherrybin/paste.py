"""Blueprint handling paste operations"""

from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from flask import Blueprint, request, redirect, url_for, g, render_template
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from cherrybin.sqids import sqids
from cherrybin.crypto import encrypt, decrypt
from cherrybin.firebase_admin import firestore_db

bp = Blueprint("paste", __name__, url_prefix="/paste")
pastes_ref = firestore_db.collection("pastes")

EXPIRY_TIMES_SECONDS = [0, 300, 600, 1800, 86400, 604800, 1209600, 18144000]
TIME_DURATION_UNITS = (
    ("month", 60 * 60 * 24 * 7 * 30),
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


def construct_expiry_values():
    options = []

    for time in EXPIRY_TIMES_SECONDS:
        options.append({"label": human_time_duration(time), "value": time})

    return options


# https://gist.github.com/borgstrom/936ca741e885a1438c374824efb038b3
def human_time_duration(seconds):
    if seconds == 0:
        return "Never"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@dataclass
class PasteMeta:
    """
    Utility fields of a Paste.
    """

    user_id: str
    created_at: datetime
    expires_at: datetime


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
            "expires_at": self.meta.expires_at,
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
        expires_at = source.get("expires_at")
        title = decrypt(source.get("title")) if encrypted else source.get("title")
        contents = (
            decrypt(source.get("contents"))
            if encrypted
            else source.get("contents", None)
        )
        return Paste(
            PasteMeta(user_id, created_at, expires_at),
            title,
            contents,
        )


@bp.post("/create")
def create():
    """Uploads paste to database"""

    timestamp = __get_current_utc_datetime()
    paste_id = sqids.encode([int(timestamp.timestamp())])
    expires_in = int(request.form["expiresIn"])
    expires_at = (timestamp + timedelta(seconds=expires_in)) if expires_in > 0 else None
    user_id = 0

    if g.user is not None:
        user_id = g.user["localId"]

    pastes_ref.document(paste_id).set(
        Paste(
            PasteMeta(user_id, timestamp, expires_at),
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
        paste_dict = paste.to_dict()
        expires_at = paste_dict["expires_at"]
        if expires_at is not None and expires_at < __get_current_utc_datetime():
            # TODO: Handle 404
            return None
        paste = Paste.from_dict(paste_dict, encrypted=True)
        return render_template("pastes/view.jinja", paste=paste)

    return render_template("home.jinja")


def __get_user_pastes(user_id):
    return (
        pastes_ref.where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=__get_current_expiration_filter())
        .select(["title", "created_at", "user_id"])
        .stream()
    )


def __get_current_utc_datetime():
    return datetime.now(tz=timezone.utc)


def __get_current_expiration_filter():
    return Or(
        filters=[
            FieldFilter("expires_at", "==", None),
            FieldFilter("expires_at", ">", __get_current_utc_datetime()),
        ]
    )
