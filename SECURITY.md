# API Security Documentation

## Overview
This API uses **API key authentication** to secure all endpoints except the health check endpoint.

## Authentication Method

### API Key Header
All requests (except `/health`) must include an API key in the request headers:

```http
X-API-Key: your-api-key-here
```

## Configuration

### Setting the API Key

#### For Development
```bash
export API_KEY="your-secret-api-key"
python app.py
```

#### For Production (with systemd)
```ini
[Service]
Environment="API_KEY=your-production-api-key"
```

#### For Docker
```bash
docker run -e API_KEY="your-secret-api-key" your-image
```

#### For Docker Compose
```yaml
environment:
  - API_KEY=your-secret-api-key
```

### Generating Secure API Keys

Use a cryptographically secure method to generate API keys:

```bash
# Option 1: Using openssl
openssl rand -hex 32

# Option 2: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 3: Using uuidgen
uuidgen
```

## Protected Endpoints

The following endpoints **require** authentication:

- `POST /chat` - Chat echo endpoint
- `POST /llm` - LLM generation endpoint
- `POST /register-device` - Device registration
- `POST /notify` - Send notifications
- `GET /devices` - List registered devices
- `POST /heartbeat` - Device heartbeat

## Public Endpoints

The following endpoints are **publicly accessible** (no API key required):

- `GET /health` - Health check (for monitoring/load balancers)

## Testing the API

### Authenticated Request Example
```bash
curl -X POST http://localhost:8600/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "Hello"}'
```

### Health Check (No Auth Required)
```bash
curl http://localhost:8600/health
```

### Testing Authentication Failure
```bash
# Missing API key - should return 401
curl -X POST http://localhost:8600/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Invalid API key - should return 401
curl -X POST http://localhost:8600/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"message": "Hello"}'
```

## Error Responses

### 401 Unauthorized
Returned when:
- API key is missing
- API key is invalid
- API key is empty

**Response:**
```json
{
  "error": "Unauthorized - valid API key required"
}
```

## Security Best Practices

### API Key Management

1. **Never commit API keys to version control**
   - Add `.env` files to `.gitignore`
   - Use environment variables

2. **Use different keys for different environments**
   - Development: `DEV_API_KEY`
   - Staging: `STAGING_API_KEY`
   - Production: `PRODUCTION_API_KEY`

3. **Rotate keys regularly**
   - Recommend monthly rotation for production
   - Implement key rotation without downtime

4. **Monitor API key usage**
   - Log authentication failures
   - Set up alerts for suspicious activity

5. **Use HTTPS in production**
   - API keys transmitted in plain HTTP can be intercepted
   - Always use TLS/SSL in production

### Additional Security Measures (Recommended)

1. **Rate Limiting**
   ```bash
   pip install flask-limiter
   ```

2. **Request Logging**
   - Log all authentication attempts
   - Track API usage per key

3. **IP Whitelisting** (optional)
   - Restrict API access to known IP addresses

4. **Multiple API Keys** (optional)
   - Issue different keys for different clients
   - Easier to revoke individual clients

## Backward Compatibility

If the `API_KEY` environment variable is **not set**, the API will:
- Log a warning message
- Allow all requests without authentication

**⚠️ This is for backward compatibility only. Always set API_KEY in production.**

## Testing

The test suite includes 13 security tests covering:
- ✅ Public endpoints (health check)
- ✅ Protected endpoints require API key
- ✅ Valid API key grants access
- ✅ Invalid API key is rejected
- ✅ Empty API key is rejected
- ✅ CORS preflight (OPTIONS) handling
- ✅ Case sensitivity of API key
- ✅ Case insensitivity of header name

Run security tests:
```bash
pytest test_security.py -v
```

## Migration Guide

If you're upgrading from an older version without authentication:

1. **Update your code to include API key in requests:**
   ```python
   headers = {"X-API-Key": "your-api-key"}
   response = requests.post(url, json=data, headers=headers)
   ```

2. **Set the API_KEY environment variable:**
   ```bash
   export API_KEY="your-generated-api-key"
   ```

3. **Restart your application**

4. **Verify authentication works:**
   ```bash
   # Should succeed
   curl -H "X-API-Key: your-api-key" http://localhost:8600/health

   # Should fail with 401
   curl http://localhost:8600/chat -d '{"message":"test"}'
   ```

## Troubleshooting

### "Unauthorized - valid API key required" Error

**Cause:** Missing or invalid API key

**Solution:**
1. Verify API_KEY environment variable is set on server
2. Verify X-API-Key header is included in request
3. Verify API key matches exactly (case-sensitive)

### Health Check Returns 401

**Cause:** Something is wrong with the authentication middleware

**Solution:**
1. Check that `request.endpoint == 'health'` check is in place
2. Verify health endpoint function name is correct
3. Check application logs for errors

### All Requests Work Without API Key

**Cause:** API_KEY environment variable is not set

**Solution:**
```bash
export API_KEY="your-secret-key"
# Restart the application
```
