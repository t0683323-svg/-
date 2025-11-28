# Ajna Hub - AI Coding Assistant Instructions

## Project Overview
Ajna Hub is a **production-ready Flask API** serving as a notification and device management hub with Firebase/Firestore integration. The project has **96.19% test coverage** with **47 automated tests** and **CI/CD via GitHub Actions**.

## Critical: Security Requirements

### 🔒 API Key Authentication (MANDATORY)
**All endpoints except `/health` require authentication.**

When generating client code, **ALWAYS** include the API key header:
```python
headers = {
    "Content-Type": "application/json",
    "X-API-Key": os.environ.get("API_KEY")  # REQUIRED for all requests
}
```

**Never:**
- ❌ Hardcode API keys in code
- ❌ Commit API keys to version control
- ❌ Generate code that omits the `X-API-Key` header

**Environment Variables Required:**
- `API_KEY` - API key for authentication (mandatory in production)
- `FIREBASE_CREDENTIALS` - Path to Firebase service account JSON (optional, defaults to `/home/ajna/ajna-hub/firebase-admin.json`)

## Architecture

### Tech Stack
- **Framework:** Flask 3.1.2 with CORS enabled
- **Database:** Google Cloud Firestore (Firebase Admin SDK 7.1.0)
- **Messaging:** Firebase Cloud Messaging (FCM)
- **External Services:** Ollama LLM (http://127.0.0.1:11434)
- **Testing:** pytest, pytest-flask, pytest-cov, pytest-mock
- **CI/CD:** GitHub Actions with 95% coverage threshold

### Project Structure
```
.
├── app.py                    # Main Flask app with core endpoints
├── routes_firebase.py        # Device registration routes (Blueprint)
├── routes_notify.py          # Notification routes (Blueprint)
├── firebase_init.py          # Firebase/Firestore initialization
├── conftest.py               # Pytest fixtures and mocks
├── test_app.py               # Tests for core endpoints (13 tests)
├── test_routes_firebase.py   # Device registration tests (7 tests)
├── test_routes_notify.py     # Notification tests (14 tests)
├── test_security.py          # Authentication tests (13 tests)
├── pytest.ini                # Pytest configuration
├── .coveragerc               # Coverage configuration
├── run_tests.sh              # Test runner script
├── TESTING.md                # Complete testing documentation
├── SECURITY.md               # Security and authentication guide
└── .github/
    └── workflows/
        └── test.yml          # CI/CD workflow (runs on every push)
```

## API Endpoints

### Public Endpoints (No Auth Required)
```python
GET /health
# Returns: {"status": "ok", "time": "2025-01-28T12:34:56.789012+00:00"}
# Purpose: Health check for load balancers/monitoring
```

### Protected Endpoints (Require X-API-Key Header)

#### Core Endpoints (app.py)
```python
POST /chat
# Body: {"message": "string"}
# Returns: {"response": "Echo: {message}"}
# Purpose: Simple echo endpoint for testing

POST /llm
# Body: {"message": "string"}
# Returns: Raw JSON from Ollama LLM service
# External: http://127.0.0.1:11434/api/generate
# Model: llama3.2:3b
# Timeout: 30 seconds
# Errors: 503 (service unavailable), 502 (empty response)
```

#### Device Management (routes_firebase.py)
```python
POST /register-device
# Body: {"device_id": "string", "fcm_token": "string (optional)"}
# Returns: {"result": "registered", "device_id": "string"}
# Firestore: Updates devices/{device_id} with {fcm_token, status: "online"}
# Behavior: Uses merge=True, allows updating existing devices
```

#### Notifications (routes_notify.py)
```python
POST /notify
# Body: {"device_id": "string", "title": "string", "body": "string"}
# Returns: {"result": "sent", "message_id": "string"}
# Purpose: Send FCM push notification to device
# Errors: 400 (missing device_id/no token), 404 (unknown device), 500 (send failure)
# Defaults: title="AJNA", body=""

GET /devices
# Returns: [{"device_id": "string", "fcm_token": "string", "status": "string", ...}]
# Purpose: List all registered devices from Firestore

POST /heartbeat
# Body: {"device_id": "string"}
# Returns: {"result": "ok", "device_id": "string"}
# Firestore: Updates devices/{device_id} with {last_seen: SERVER_TIMESTAMP, status: "online"}
```

## Code Conventions

### Adding New Routes
**Always follow this pattern:**
```python
# In app.py or a Blueprint
@app.route("/new-endpoint", methods=["POST"])
def new_endpoint():
    # 1. Get request data
    data = request.json or {}

    # 2. Validate required fields
    required_field = data.get("required_field")
    if not required_field:
        return jsonify({"error": "required_field is required"}), 400

    # 3. Perform business logic
    result = do_something(required_field)

    # 4. Return JSON response
    return jsonify({"result": result})
```

**Note:** Authentication is handled globally by `@app.before_request` middleware. Don't add auth checks to individual routes.

### Response Patterns
- **Success:** `return jsonify({...}), 200` (200 is default, can be omitted)
- **Client Error:** `return jsonify({"error": "message"}), 400`
- **Not Found:** `return jsonify({"error": "message"}), 404`
- **Server Error:** `return jsonify({"error": "message"}), 500`
- **Unauthorized:** `return jsonify({"error": "Unauthorized"}), 401` (handled by middleware)

### Timestamps
- Use **UTC with timezone:** `datetime.now(tz=timezone.utc).isoformat()`
- Firestore timestamps: Use `firestore.SERVER_TIMESTAMP`

## Testing Requirements

### Running Tests
```bash
# Quick run with our custom script
./run_tests.sh --verbose --html

# Or use pytest directly
pytest -v --cov=. --cov-report=term --cov-report=html

# Run specific test file
pytest test_security.py -v
```

### Writing Tests
**Always use the provided fixtures from conftest.py:**

```python
def test_example(client, mock_firestore, sample_device_data):
    """Test description here."""
    # client - Authenticated Flask test client (includes API key automatically)
    # mock_firestore - Mocked Firestore database
    # sample_device_data - Sample device registration data

    response = client.post('/endpoint',
                           json={'key': 'value'},
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data['expected_key'] == 'expected_value'
```

**Available Fixtures:**
- `client` - Authenticated test client (includes API key)
- `unauthorized_client` - Test client without API key (for testing auth failures)
- `mock_firestore` - Mocked Firestore database
- `mock_fcm` - Mocked Firebase Cloud Messaging
- `sample_device_data` - Sample device data
- `sample_notification_data` - Sample notification data

### Test Organization
- **test_app.py** - Core endpoint tests (health, chat, llm)
- **test_routes_firebase.py** - Device registration tests
- **test_routes_notify.py** - Notification, device list, heartbeat tests
- **test_security.py** - Authentication and security tests

**Coverage Requirement:** Minimum 95% (enforced by CI/CD)

## Firebase/Firestore Integration

### Initialization (firebase_init.py)
```python
# Uses environment variable for credential path
cred_path = os.getenv("FIREBASE_CREDENTIALS", "/home/ajna/ajna-hub/firebase-admin.json")
cred = credentials.Certificate(cred_path)

# Singleton pattern - only initializes once
firebase_admin.initialize_app(cred)
db = firestore.client()
```

### Database Operations
**All Firestore operations are automatically mocked in tests.**

When adding Firestore code:
```python
# Read document
doc = db.collection('devices').document(device_id).get()
if doc.exists:
    data = doc.to_dict()

# Write document (use merge=True for updates)
db.collection('devices').document(device_id).set({
    'field': 'value'
}, merge=True)

# List documents
docs = db.collection('devices').stream()
for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')
```

### FCM (Firebase Cloud Messaging)
```python
from firebase_admin import messaging

# Send notification
message = messaging.Message(
    notification=messaging.Notification(
        title='Title',
        body='Message body'
    ),
    token=fcm_token
)
message_id = messaging.send(message)
```

## External Services

### Ollama LLM Service
- **Endpoint:** http://127.0.0.1:11434/api/generate
- **Model:** llama3.2:3b
- **Timeout:** 30 seconds
- **Error Handling:** Always wrap in try/except for RequestException

```python
try:
    r = requests.post("http://127.0.0.1:11434/api/generate",
                      timeout=30,
                      json={"model": "llama3.2:3b", "prompt": msg})
    r.raise_for_status()
    return r.text, r.status_code, {"Content-Type": "application/json"}
except requests.exceptions.RequestException as e:
    app.logger.error("LLM service error: %s", str(e))
    return jsonify({"error": "LLM service unavailable"}), 503
```

## CI/CD Pipeline

### GitHub Actions Workflow
- **Triggers:** Push to main/master/develop/claude/* branches, PRs
- **Python Versions:** 3.11, 3.12 (matrix testing)
- **Coverage Threshold:** 95% minimum (build fails if lower)
- **Artifacts:** HTML coverage reports (30-day retention)

### Pre-Commit Checklist
Before committing code:
1. ✅ Run tests: `./run_tests.sh`
2. ✅ Check coverage: Must be ≥95%
3. ✅ No hardcoded secrets or API keys
4. ✅ Update tests for any new endpoints
5. ✅ Update this file if API changes

## Security Best Practices

### API Key Management
```bash
# Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment (never commit this)
export API_KEY="your-generated-key-here"
export FIREBASE_CREDENTIALS="/path/to/service-account.json"
```

### Client Code Generation
**Always include authentication:**
```python
import os
import requests

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

def call_api(endpoint, data):
    response = requests.post(
        f"http://localhost:8600{endpoint}",
        json=data,
        headers={"X-API-Key": API_KEY}
    )
    response.raise_for_status()
    return response.json()
```

### CORS Configuration
CORS is enabled globally for all routes:
```python
CORS(app)  # Allows all origins (consider restricting in production)
```

## Common Patterns

### Adding a New Protected Endpoint
1. Define route in appropriate file (app.py or Blueprint)
2. Add input validation
3. Implement business logic
4. Return JSON response
5. **Write tests** in corresponding test file
6. Run `./run_tests.sh` to verify coverage

### Example: Adding a New Endpoint
```python
# In app.py or routes_*.py
@app.route("/new-feature", methods=["POST"])
def new_feature():
    data = request.json or {}

    # Validation
    param = data.get("param")
    if not param:
        return jsonify({"error": "param is required"}), 400

    # Business logic
    result = process_param(param)

    # Response
    return jsonify({"result": result})

# In test_app.py or test_routes_*.py
def test_new_feature(client):
    """Test new feature endpoint."""
    response = client.post('/new-feature',
                           json={'param': 'value'},
                           content_type='application/json')
    assert response.status_code == 200
    assert response.get_json()['result'] == 'expected'

def test_new_feature_missing_param(client):
    """Test new feature with missing param."""
    response = client.post('/new-feature',
                           json={},
                           content_type='application/json')
    assert response.status_code == 400
```

## Deployment

### Local Development
```bash
export API_KEY="development-key-123"
export FIREBASE_CREDENTIALS="/path/to/dev-credentials.json"
python app.py
# Server runs on http://127.0.0.1:8600
```

### Production Considerations
- Set `API_KEY` environment variable (use secrets management)
- Use HTTPS (terminate TLS at load balancer or reverse proxy)
- Consider restricting CORS to specific origins
- Set up monitoring/alerting
- Use production Firebase project credentials
- Consider rate limiting (flask-limiter)

## Documentation
- **TESTING.md** - Complete testing guide (how to run tests, fixtures, coverage)
- **SECURITY.md** - Security guide (API key setup, examples, troubleshooting)
- **This file** - Source of truth for development patterns

## Questions/Clarifications Needed
None - project is fully documented and production-ready.

## Changelog
- **2025-01-28:** Complete rewrite to reflect current architecture
  - Added 7 endpoints (was showing only 3)
  - Documented API key authentication
  - Added test suite documentation (47 tests, 96.19% coverage)
  - Documented CI/CD pipeline
  - Added Firebase/Firestore integration details
  - Added security best practices
