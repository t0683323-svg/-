# Client Integration Guide

## Overview
After implementing API key authentication, all clients must include the `X-API-Key` header in requests to protected endpoints.

## Python Clients

### Basic Python Request
```python
import os
import requests

# Load API key from environment
API_KEY = os.environ.get("API_KEY")
BASE_URL = "http://localhost:8600"  # Or your production URL

def send_notification(device_id, title, body):
    """Send notification to a device."""
    response = requests.post(
        f"{BASE_URL}/notify",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY  # REQUIRED
        },
        json={
            "device_id": device_id,
            "title": title,
            "body": body
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
result = send_notification("device-123", "Alert", "Motion detected")
print(f"Notification sent: {result['message_id']}")
```

### Reusable API Client Class
```python
import os
import requests
from typing import Optional, Dict, Any

class AjnaHubClient:
    """Client for Ajna Hub API with automatic API key authentication."""

    def __init__(self, base_url: str = "http://localhost:8600", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.environ.get("API_KEY")

        if not self.api_key:
            raise ValueError("API_KEY must be provided or set in environment")

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        })

    def register_device(self, device_id: str, fcm_token: Optional[str] = None) -> Dict[str, Any]:
        """Register a device with optional FCM token."""
        response = self.session.post(
            f"{self.base_url}/register-device",
            json={"device_id": device_id, "fcm_token": fcm_token}
        )
        response.raise_for_status()
        return response.json()

    def send_notification(self, device_id: str, title: str = "AJNA", body: str = "") -> Dict[str, Any]:
        """Send push notification to a device."""
        response = self.session.post(
            f"{self.base_url}/notify",
            json={
                "device_id": device_id,
                "title": title,
                "body": body
            }
        )
        response.raise_for_status()
        return response.json()

    def heartbeat(self, device_id: str) -> Dict[str, Any]:
        """Send heartbeat for a device."""
        response = self.session.post(
            f"{self.base_url}/heartbeat",
            json={"device_id": device_id}
        )
        response.raise_for_status()
        return response.json()

    def list_devices(self) -> list:
        """List all registered devices."""
        response = self.session.get(f"{self.base_url}/devices")
        response.raise_for_status()
        return response.json()

    def chat(self, message: str) -> Dict[str, Any]:
        """Send message to chat endpoint."""
        response = self.session.post(
            f"{self.base_url}/chat",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()

    def llm(self, message: str) -> str:
        """Send message to LLM endpoint."""
        response = self.session.post(
            f"{self.base_url}/llm",
            json={"message": message}
        )
        response.raise_for_status()
        return response.text

    def health_check(self) -> Dict[str, Any]:
        """Check API health (no auth required)."""
        # Health endpoint doesn't require auth, but our session header won't hurt
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage Example
if __name__ == "__main__":
    # Initialize client (API_KEY from environment)
    client = AjnaHubClient(base_url="http://localhost:8600")

    # Register device
    result = client.register_device("my-device-001", "fcm-token-xyz")
    print(f"Device registered: {result}")

    # Send notification
    result = client.send_notification(
        "my-device-001",
        title="Security Alert",
        body="Motion detected in garage"
    )
    print(f"Notification sent: {result['message_id']}")

    # Send heartbeat
    client.heartbeat("my-device-001")
    print("Heartbeat sent")

    # List all devices
    devices = client.list_devices()
    print(f"Total devices: {len(devices)}")
```

## Home Assistant Integration

### RESTful Command (YAML)
```yaml
# configuration.yaml
rest_command:
  ajna_notify:
    url: "http://YOUR_HUB_IP:8600/notify"
    method: POST
    headers:
      Content-Type: "application/json"
      X-API-Key: !secret ajna_api_key  # Store in secrets.yaml
    payload: >
      {
        "device_id": "{{ device_id }}",
        "title": "{{ title }}",
        "body": "{{ body }}"
      }

  ajna_heartbeat:
    url: "http://YOUR_HUB_IP:8600/heartbeat"
    method: POST
    headers:
      Content-Type: "application/json"
      X-API-Key: !secret ajna_api_key
    payload: >
      {
        "device_id": "{{ device_id }}"
      }
```

```yaml
# secrets.yaml
ajna_api_key: "your-actual-api-key-here"
```

### Automation Example
```yaml
# automations.yaml
- alias: "Notify on Motion Detected"
  trigger:
    - platform: state
      entity_id: binary_sensor.garage_motion
      to: "on"
  action:
    - service: rest_command.ajna_notify
      data:
        device_id: "home-assistant-device"
        title: "Motion Alert"
        body: "Motion detected in garage at {{ now().strftime('%H:%M') }}"

- alias: "Send Heartbeat Every 5 Minutes"
  trigger:
    - platform: time_pattern
      minutes: "/5"
  action:
    - service: rest_command.ajna_heartbeat
      data:
        device_id: "home-assistant-device"
```

### RESTful Sensor (for device list)
```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "Ajna Devices"
    resource: "http://YOUR_HUB_IP:8600/devices"
    method: GET
    headers:
      X-API-Key: !secret ajna_api_key
    value_template: "{{ value_json | length }}"
    json_attributes:
      - device_id
      - status
      - fcm_token
    scan_interval: 300  # Update every 5 minutes
```

## Node.js / JavaScript Client

### Using Fetch (Node.js 18+)
```javascript
// ajnaClient.js
const AJNA_API_KEY = process.env.API_KEY;
const BASE_URL = 'http://localhost:8600';

class AjnaClient {
  constructor(apiKey = AJNA_API_KEY, baseUrl = BASE_URL) {
    if (!apiKey) {
      throw new Error('API_KEY is required');
    }
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  async request(endpoint, method = 'GET', body = null) {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      }
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }

    return response.json();
  }

  async registerDevice(deviceId, fcmToken = null) {
    return this.request('/register-device', 'POST', {
      device_id: deviceId,
      fcm_token: fcmToken
    });
  }

  async sendNotification(deviceId, title = 'AJNA', body = '') {
    return this.request('/notify', 'POST', {
      device_id: deviceId,
      title,
      body
    });
  }

  async heartbeat(deviceId) {
    return this.request('/heartbeat', 'POST', { device_id: deviceId });
  }

  async listDevices() {
    return this.request('/devices');
  }
}

// Usage
const client = new AjnaClient();

client.sendNotification('device-123', 'Alert', 'Motion detected')
  .then(result => console.log('Sent:', result.message_id))
  .catch(err => console.error('Error:', err.message));
```

## ESP32 / Arduino (C++)

### Using HTTPClient
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "your-wifi-ssid";
const char* password = "your-wifi-password";
const char* ajnaUrl = "http://192.168.1.100:8600";
const char* apiKey = "your-api-key-here";

String deviceId = "esp32-device-001";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Register device on startup
  registerDevice(deviceId);
}

void loop() {
  // Send heartbeat every 5 minutes
  sendHeartbeat(deviceId);
  delay(300000);  // 5 minutes
}

void registerDevice(String devId) {
  HTTPClient http;
  http.begin(String(ajnaUrl) + "/register-device");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);  // CRITICAL: Add API key

  StaticJsonDocument<200> doc;
  doc["device_id"] = devId;
  doc["fcm_token"] = "";  // Optional

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);

  if (httpCode == 200) {
    Serial.println("Device registered successfully");
  } else {
    Serial.printf("Registration failed: %d\n", httpCode);
    Serial.println(http.getString());
  }

  http.end();
}

void sendHeartbeat(String devId) {
  HTTPClient http;
  http.begin(String(ajnaUrl) + "/heartbeat");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);  // CRITICAL: Add API key

  StaticJsonDocument<100> doc;
  doc["device_id"] = devId;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);

  if (httpCode == 200) {
    Serial.println("Heartbeat sent");
  } else {
    Serial.printf("Heartbeat failed: %d\n", httpCode);
  }

  http.end();
}

void sendNotification(String devId, String title, String body) {
  HTTPClient http;
  http.begin(String(ajnaUrl) + "/notify");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);  // CRITICAL: Add API key

  StaticJsonDocument<300> doc;
  doc["device_id"] = devId;
  doc["title"] = title;
  doc["body"] = body;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);

  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("Notification sent: " + response);
  } else {
    Serial.printf("Notification failed: %d\n", httpCode);
  }

  http.end();
}
```

## Shell Script / cURL

### Bash Functions
```bash
#!/bin/bash

# Configuration
API_KEY="${API_KEY:-your-api-key-here}"
BASE_URL="${AJNA_URL:-http://localhost:8600}"

# Helper function for API calls
ajna_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"

    if [ "$method" = "GET" ]; then
        curl -s -X "$method" \
            -H "X-API-Key: $API_KEY" \
            "$BASE_URL$endpoint"
    else
        curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d "$data" \
            "$BASE_URL$endpoint"
    fi
}

# Register device
ajna_register_device() {
    local device_id="$1"
    local fcm_token="${2:-}"

    ajna_api "/register-device" "POST" \
        "{\"device_id\":\"$device_id\",\"fcm_token\":\"$fcm_token\"}"
}

# Send notification
ajna_notify() {
    local device_id="$1"
    local title="$2"
    local body="$3"

    ajna_api "/notify" "POST" \
        "{\"device_id\":\"$device_id\",\"title\":\"$title\",\"body\":\"$body\"}"
}

# Send heartbeat
ajna_heartbeat() {
    local device_id="$1"
    ajna_api "/heartbeat" "POST" "{\"device_id\":\"$device_id\"}"
}

# List devices
ajna_list_devices() {
    ajna_api "/devices" "GET" | jq .
}

# Health check
ajna_health() {
    ajna_api "/health" "GET" | jq .
}

# Usage examples
# ajna_register_device "my-device-001" "fcm-token-xyz"
# ajna_notify "my-device-001" "Alert" "Motion detected"
# ajna_heartbeat "my-device-001"
# ajna_list_devices
```

## Docker Environment Variables

### Docker Run
```bash
docker run -d \
  -e API_KEY="your-secure-api-key" \
  -e AJNA_HUB_URL="http://ajna-hub:8600" \
  your-client-image
```

### Docker Compose
```yaml
version: '3.8'

services:
  ajna-hub:
    build: .
    environment:
      - API_KEY=${AJNA_API_KEY}
      - FIREBASE_CREDENTIALS=/app/credentials.json
    ports:
      - "8600:8600"

  client-app:
    build: ./client
    environment:
      - API_KEY=${AJNA_API_KEY}  # Same key as hub
      - AJNA_HUB_URL=http://ajna-hub:8600
    depends_on:
      - ajna-hub
```

```bash
# .env file (DO NOT COMMIT)
AJNA_API_KEY=your-generated-api-key-here
```

## Testing Client Authentication

### Verify API Key Works
```bash
# Should succeed (200 OK)
curl -X POST http://localhost:8600/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "test"}'

# Should fail (401 Unauthorized)
curl -X POST http://localhost:8600/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Troubleshooting

### Common Errors

**401 Unauthorized**
```
{"error": "Unauthorized - valid API key required"}
```
**Solution:** Add `X-API-Key` header with correct key

**Connection Refused**
```
requests.exceptions.ConnectionError: Connection refused
```
**Solution:** Verify hub is running and URL is correct

**Missing API Key in Environment**
```
ValueError: API_KEY must be provided or set in environment
```
**Solution:** Set `API_KEY` environment variable

## Migration Checklist

When updating existing clients:

1. ✅ Generate secure API key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. ✅ Set API_KEY on server and restart
3. ✅ Update all client code to include `X-API-Key` header
4. ✅ Store API key securely (environment variables, secrets manager)
5. ✅ Test each client individually
6. ✅ Monitor logs for 401 errors
7. ✅ Update documentation for other developers
