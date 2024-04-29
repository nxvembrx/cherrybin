"""Blueprint handling pasta operations"""

import time
from flask import Blueprint, request, redirect, url_for, g
from instapasta.pyrebase import firebase_db
from instapasta.auth import login_required

bp = Blueprint("pasta", __name__, url_prefix="/pasta")


@bp.post("/create")
@login_required
def create():
    """Uploads pasta to database"""

    pasta_data = {
        "contents": request.form["pastaText"],
        "created_at": time.time(),
        "user_id": g.user["localId"],
    }
    firebase_db.child("pasta").push(pasta_data, g.user["idToken"])
    return redirect(url_for("index"))
