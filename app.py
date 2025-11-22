"""Flask application with health, chat, and LLM endpoints."""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import requests
from routes_firebase import bp_firebase
from routes_notify import bp_notify

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.register_blueprint(bp_firebase)
app.register_blueprint(bp_notify)

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status":"ok","time":datetime.now(tz=timezone.utc).isoformat()})

@app.route("/chat", methods=["POST"])
def chat():
    """Echo chat endpoint."""
    data = request.json or {}
    msg = data.get("message","")
    if not msg:
        return jsonify({"error": "message field is required"}), 400
    return jsonify({"response":f"Echo: {msg}"} )

@app.route("/llm", methods=["POST"])
def llm():
    """LLM generation endpoint."""
    data = request.json or {}
    msg = data.get("message","")
    if not msg:
        return jsonify({"error": "message field is required"}), 400
    payload = {
        "model":"llama3.2:3b",
        "prompt": msg
    }
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate", timeout=30, json=payload)
        r.raise_for_status()
        if r.text:
            return r.text, r.status_code, {"Content-Type":"application/json"}
        return jsonify({"error": "Empty response from LLM service"}), 502
    except requests.exceptions.RequestException as e:
        app.logger.error("LLM service error: %s", str(e))
        return jsonify({"error": "LLM service unavailable"}), 503

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8600)
