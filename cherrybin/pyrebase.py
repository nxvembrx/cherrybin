import os
from dotenv import load_dotenv
import pyrebase

load_dotenv()

BASE_API_KEY = os.getenv("BASE_API_KEY")
BASE_AUTH_DOMAIN = os.getenv("BASE_AUTH_DOMAIN")
BASE_DB_URL = os.getenv("BASE_DB_URL")
BASE_BUCKET = os.getenv("BASE_BUCKET")


config = {
    "apiKey": BASE_API_KEY,
    "authDomain": BASE_AUTH_DOMAIN,
    "databaseURL": BASE_DB_URL,
    "storageBucket": BASE_BUCKET,
    # https://github.com/thisbejim/Pyrebase/issues/52#issuecomment-298182589
    "serviceAccount": {
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "type": "service_account",
    },
}

firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()
firebase_db = firebase.database()
