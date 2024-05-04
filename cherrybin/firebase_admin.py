import os
import firebase_admin
from firebase_admin import firestore

credentials = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace(r"\n", "\n"),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": os.environ.get(
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL"
    ),
    "client_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL"),
}

certificate = firebase_admin.credentials.Certificate(credentials)
firebase = firebase_admin.initialize_app(certificate)
firestore_db = firestore.client()
