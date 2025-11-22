from flask import Blueprint, request, jsonify
from firebase_init import db
from firebase_admin import messaging, firestore

bp_notify = Blueprint('notify', __name__)
@bp_notify.route("/notify", methods=["POST"])
def notify():
    data = request.json or {}
    device_id = data.get('device_id')
    title = data.get('title', 'AJNA')
    body = data.get('body', '')
    if not device_id: return jsonify({'error':'missing device_id'}), 400
    doc = db.collection('devices').document(device_id).get()
    if not doc.exists: return jsonify({'error':'unknown device'}), 404
    token = doc.to_dict().get('fcm_token')
    if not token: return jsonify({'error':'no fcm_token for device'}), 400
    msg = messaging.Message(notification=messaging.Notification(title=title, body=body), token=token)
    try:
        message_id = messaging.send(msg)
        return jsonify({'result':'sent','message_id':message_id})
    except Exception as e: return jsonify({'error':str(e)}), 500
@bp_notify.route("/devices", methods=["GET"])
def devices():
    docs = db.collection('devices').stream()
    out = []
    for d in docs: item=d.to_dict(); item['device_id']=d.id; out.append(item)
    return jsonify(out)
@bp_notify.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json or {}
    device_id = data.get('device_id')
    if not device_id: return jsonify({'error':'missing device_id'}), 400
    db.collection('devices').document(device_id).set({'last_seen':firestore.SERVER_TIMESTAMP,'status':'online'}, merge=True)
    return jsonify({'result':'ok','device_id':device_id})
