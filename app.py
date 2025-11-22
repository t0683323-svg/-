from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

@app.route("/status")
def status():
    return jsonify({"hub": "online"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    msg = data.get("message", "")
    return jsonify({"response": f"Echo AI: {msg}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8600)
