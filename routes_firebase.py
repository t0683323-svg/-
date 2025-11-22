"""Firebase routes for device registration."""
from flask import Blueprint, request, jsonify
from firebase_init import db

bp_firebase = Blueprint("firebase", __name__)

@bp_firebase.route("/register-device", methods=["POST"])
def register_device():
    """Register device with FCM token."""
    data = request.json or {}
    device_id = data.get("device_id")
    token = data.get("fcm_token")

    if not device_id:
        return jsonify({"error": "missing device_id"}), 400

    db.collection("devices").document(device_id).set({
        "fcm_token": token,
        "status": "online"
    }, merge=True)

    return jsonify({"result": "registered", "device_id": device_id})
