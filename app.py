"""Flask application with health, chat, and LLM endpoints."""
import os
import time
import platform
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import requests
from routes_firebase import bp_firebase
from routes_notify import bp_notify

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.register_blueprint(bp_firebase)
app.register_blueprint(bp_notify)

# Track application start time for uptime calculation
start_time = time.time()


@app.before_request
def require_api_key():
    """Verify API key for all requests except health check and OPTIONS."""
    # Allow OPTIONS requests (for CORS preflight)
    if request.method == 'OPTIONS':
        return

    # Allow health check and admin dashboard without authentication
    # (dashboard has its own auth via query parameter)
    if request.endpoint in ['health', 'admin_dashboard']:
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


@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    """Admin dashboard showing system metrics and status."""
    # Allow authentication via header OR query parameter (for browser convenience)
    api_key = request.headers.get('X-API-Key') or request.args.get('key')
    expected_key = os.environ.get('API_KEY')

    # Require authentication for dashboard
    if not expected_key or api_key != expected_key:
        return jsonify({"error": "Unauthorized - API key required"}), 401

    try:
        # Import psutil and git here (lazy import for optional dependencies)
        import psutil
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            version = repo.head.object.hexsha[:7]
        except Exception:
            version = "unknown"

        # System metrics
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Uptime calculation
        uptime_seconds = time.time() - start_time
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))

        # Device count from Firestore
        try:
            from firebase_init import db
            devices_ref = db.collection('devices')
            device_count = len(list(devices_ref.stream()))
        except Exception as e:
            app.logger.warning(f"Could not fetch device count: {e}")
            device_count = "N/A"

        # Compile dashboard data
        data = {
            'version': version,
            'uptime': uptime_str,
            'cpu_percent': round(cpu, 1),
            'memory_percent': round(mem.percent, 1),
            'memory_used': round(mem.used / (1024**3), 2),
            'memory_total': round(mem.total / (1024**3), 2),
            'disk_percent': round(disk.percent, 1),
            'device_count': device_count,
            'python_version': platform.python_version(),
            'platform': platform.system(),
            'api_key': api_key,  # Pass to template for JSON link
            'current_time': datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        }

        # Return JSON or HTML based on format parameter
        if request.args.get('format') == 'json':
            # Remove sensitive data from JSON response
            json_data = data.copy()
            json_data.pop('api_key', None)
            return jsonify(json_data)

        return render_template('dashboard.html', **data)

    except ImportError as e:
        return jsonify({
            'error': 'Dashboard dependencies not installed',
            'details': str(e),
            'help': 'Run: pip install psutil gitpython'
        }), 500
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8600)
