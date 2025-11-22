# Ajna Hub - Copilot Instructions

## Project Overview
Ajna Hub is a minimal Flask-based API service serving as a communication hub. The service provides health checks, status endpoints, and a simple chat echo interface.

## Architecture

### Core Components
- **Single-file Flask application** (`app.py`) - All routes and logic in one file
- **Firebase/Google Cloud integration** - Dependencies installed for Firebase Admin SDK, Cloud Firestore, and Cloud Storage
- **RESTful API** - JSON-based request/response pattern

### Key Endpoints
```python
GET  /health  # Health check with UTC timestamp
GET  /status  # Hub online status
POST /chat    # Echo chat endpoint (returns "Echo AI: {message}")
```

## Development Environment

### Python Setup
- Python 3.10 in a venv at `./venv/`
- Flask 3.1.2 as the web framework
- Firebase Admin 7.1.0 for potential Firebase operations
- Google Cloud libraries (Firestore 2.21.0, Storage 3.6.0) installed but not yet used in code

### Running the Service
```bash
# Activate venv (if not active)
source venv/bin/activate

# Run the Flask app
python app.py

# Service runs on 0.0.0.0:8600
```

### Testing Endpoints
```bash
curl http://localhost:8600/health
curl http://localhost:8600/status
curl -X POST http://localhost:8600/chat -H "Content-Type: application/json" -d '{"message": "test"}'
```

## Code Conventions

### Response Pattern
- All endpoints return JSON via `jsonify()`
- Use ISO 8601 format for timestamps: `datetime.utcnow().isoformat()`
- POST endpoints access data via `request.json or {}`

### Route Organization
- Routes defined directly on Flask app instance using `@app.route()`
- HTTP methods specified in decorator: `@app.route("/chat", methods=["POST"])`

### Error Handling
- Currently minimal - add defensive checks when handling user input
- Return appropriate HTTP status codes with JSON error responses

## Integration Points

### Firebase/Google Cloud (Not Yet Active)
The venv includes Firebase Admin SDK and Google Cloud libraries, suggesting future integration:
- `firebase_admin` - For Firebase Authentication or Realtime Database
- `google.cloud.firestore` - For document database operations  
- `google.cloud.storage` - For file/blob storage

**When adding Firebase/GCP features:**
1. Initialize Firebase Admin with service account credentials
2. Store credentials outside version control (`.env` or secrets)
3. Add error handling for network/authentication failures

## Project Structure
```
ajna-hub/
├── app.py              # Main Flask application
├── venv/               # Python virtual environment (don't modify)
├── __pycache__/        # Python cache (don't modify)
└── .github/            # GitHub configuration
    └── copilot-instructions.md
```

## Key Patterns

### Adding New Routes
Follow the existing pattern in `app.py`:
```python
@app.route("/endpoint", methods=["GET"])  # or ["POST", "PUT", etc.]
def endpoint_name():
    # Access JSON data for POST: data = request.json or {}
    # Return JSON: return jsonify({"key": "value"})
    pass
```

### Port Configuration
The service binds to **port 8600** on all interfaces (`0.0.0.0`). Change the port in `app.run()` if needed.

## Questions to Clarify
1. **Firebase Usage**: Are Firebase/Firestore features planned? Should we initialize Firebase Admin?
2. **Authentication**: Will endpoints need auth? JWT tokens? Firebase Auth?
3. **Chat Logic**: Is the `/chat` echo response temporary? What's the intended behavior?
4. **Deployment**: How will this be deployed? Docker? Cloud Run? Traditional server?
5. **Dependencies**: Should we create `requirements.txt` for reproducible installs?
