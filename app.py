"""Flask application with health, chat, and LLM endpoints."""
import os
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


@app.before_request
def require_api_key():
    """Verify API key for all requests except health check and OPTIONS."""
    # Allow OPTIONS requests (for CORS preflight)
    if request.method == 'OPTIONS':
        return

    # Allow health check without authentication (for monitoring)
    if request.endpoint == 'health':
        return

    # Get API key from request headers
    api_key = request.headers.get('X-API-Key')
    expected_key = os.environ.get('API_KEY')

    # If API_KEY is not configured, allow requests (backward compatibility)
    # In production, you should make this mandatory by removing this check
    if not expected_key:
        app.logger.warning("API_KEY environment variable not set - authentication disabled")
        return

    # Verify API key
    if api_key != expected_key:
        return jsonify({'error': 'Unauthorized - valid API key required'}), 401

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
