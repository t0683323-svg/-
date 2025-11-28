import firebase_admin
from firebase_admin import credentials, firestore
import os

# Use environment variable for credential path, fallback to default location
cred_path = os.getenv("FIREBASE_CREDENTIALS", "/home/ajna/ajna-hub/firebase-admin.json")
cred = credentials.Certificate(cred_path)

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()
