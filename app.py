from flask import Flask, request, jsonify
from datetime import datetime, timezone
import requests
from routes_firebase import bp_firebase

app = Flask(__name__)
app.register_blueprint(bp_firebase)

@app.route("/health")
def health():
    return jsonify({"status":"ok","time":datetime.now(timezone.utc).isoformat()})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    msg = data.get("message","")
    return jsonify({"response":f"Echo: {msg}"} )

@app.route("/llm", methods=["POST"])
def llm():
    data = request.json or {}
    payload = {
        "model":"llama3.2:3b",
        "prompt": data.get("message","")
    }
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=30)
        return r.text, r.status_code, {"Content-Type":"application/json"}
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "LLM service unavailable"}), 503

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8600)
