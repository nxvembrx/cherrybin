"""Blueprint handling pasta operations"""

import time
from datetime import datetime
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

    pasta_response = (
        firebase_db.child("pasta")
        .child(g.user["localId"])
        .shallow()
        .get(g.user["idToken"])
    )

    pasta_list = []

    for pasta in pasta_response.val():
        timestamp = int(pasta[0:10])
        name = pasta[10:]

        pasta_list.append((name, datetime.fromtimestamp(timestamp)))

    return render_template("pastas/my.jinja", pastas=pasta_list)
