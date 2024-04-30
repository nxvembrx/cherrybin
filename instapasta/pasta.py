"""Blueprint handling pasta operations"""

import time
from base64 import b64encode, b64decode
from flask import Blueprint, request, redirect, url_for, g, render_template
from instapasta.pyrebase import firebase_db
from instapasta.auth import login_required

bp = Blueprint("pasta", __name__, url_prefix="/pasta")


@bp.post("/create")
@login_required
def create():
    """Uploads pasta to database"""

    pasta_name = request.form["pastaName"] if request.form["pastaName"] else "Unnamed"
    timestamp = int(time.time())
    pasta_id = str(timestamp) + pasta_name

    pasta_data = {"contents": request.form["pastaText"]}

    firebase_db.child("pasta").child(g.user["localId"]).child(pasta_id).push(
        pasta_data, g.user["idToken"]
    )

    return redirect(url_for("index"))


@bp.get("/my")
@login_required
def my_pastas():
    """Get a list of current user's pastas"""

    user_id = g.user["localId"]

    pasta_response = (
        firebase_db.child("pasta").child(user_id).shallow().get(g.user["idToken"])
    )

    pasta_list = []

    for pasta_key in pasta_response.val():
        timestamp = pasta_key[0:10]
        name = pasta_key[10:]
        pasta_id = b64encode((user_id + pasta_key).encode("ascii")).decode("ascii")

        pasta_list.append({"name": name, "timestamp": int(timestamp), "id": pasta_id})

    return render_template("pastas/my.jinja", pastas=pasta_list)


@bp.get("/get/<string:id>")
@login_required
def get(id):
    """Get the pasta by its id"""

    decoded_id = b64decode(id.encode("ascii")).decode("ascii")

    user_id = decoded_id[0:28]
    timestamp = decoded_id[28:38]
    name = decoded_id[38:]

    pasta_response = (
        firebase_db.child("pasta")
        .child(user_id)
        .child(timestamp + name)
        .get(g.user["idToken"])
    )

    pasta = {
        "name": name,
        "timestamp": int(timestamp),
        "contents": pasta_response.val()["contents"],
    }

    return render_template("pastas/view.jinja", pasta=pasta)
