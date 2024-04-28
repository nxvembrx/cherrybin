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
}

firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()
