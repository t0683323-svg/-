import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("/home/ajna/ajna-hub/firebase-admin.json")

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()
