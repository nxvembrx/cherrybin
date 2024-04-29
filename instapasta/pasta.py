"""Blueprint handling pasta operations"""

import time
from flask import Blueprint, request, redirect, url_for, g, render_template
from instapasta.pyrebase import firebase_db
from instapasta.auth import login_required

bp = Blueprint("pasta", __name__, url_prefix="/pasta")


@bp.post("/create")
@login_required
def create():
    """Uploads pasta to database"""

    pasta_data = {
        "name": request.form["pastaName"] if request.form["pastaName"] else "Unnamed",
        "contents": request.form["pastaText"],
        "created_at": time.time(),
    }
    firebase_db.child("pasta").child(g.user["localId"]).push(
        pasta_data, g.user["idToken"]
    )
    return redirect(url_for("index"))


@bp.get("/my")
@login_required
def my_pastas():
    """Get a list of current user's pastas"""

    pastas_response = (
        firebase_db.child("pasta")
        .child(g.user["localId"])
        .shallow()
        .get(g.user["idToken"])
    )

    return render_template("pastas/my.jinja", pastas=pastas_response.val())
