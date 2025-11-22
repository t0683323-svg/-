from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"ok","time":datetime.utcnow().isoformat()})

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
    r = requests.post("http://127.0.0.1:11434/api/generate", json=payload)
    return r.text, r.status_code, {"Content-Type":"application/json"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8600)
