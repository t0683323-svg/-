"""Tests for API key authentication and security."""
import os


class TestAPIKeyAuthentication:
    """Tests for API key authentication middleware."""

    def test_health_endpoint_public(self, unauthorized_client):
        """Test that health endpoint is publicly accessible without API key."""
        response = unauthorized_client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_chat_requires_api_key(self, unauthorized_client):
        """Test that chat endpoint requires API key."""
        response = unauthorized_client.post('/chat',
                                             json={'message': 'test'},
                                             content_type='application/json')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Unauthorized' in data['error']

    def test_chat_with_valid_api_key(self, client):
        """Test that chat endpoint works with valid API key."""
        response = client.post('/chat',
                               json={'message': 'test'},
                               content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data

    def test_llm_requires_api_key(self, unauthorized_client):
        """Test that LLM endpoint requires API key."""
        response = unauthorized_client.post('/llm',
                                             json={'message': 'test'},
                                             content_type='application/json')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Unauthorized' in data['error']

    def test_register_device_requires_api_key(self, unauthorized_client):
        """Test that device registration requires API key."""
        response = unauthorized_client.post('/register-device',
                                             json={'device_id': 'test-123'},
                                             content_type='application/json')
        assert response.status_code == 401

    def test_notify_requires_api_key(self, unauthorized_client):
        """Test that notify endpoint requires API key."""
        response = unauthorized_client.post('/notify',
                                             json={
                                                 'device_id': 'test-123',
                                                 'title': 'Test',
                                                 'body': 'Test'
                                             },
                                             content_type='application/json')
        assert response.status_code == 401

    def test_devices_list_requires_api_key(self, unauthorized_client):
        """Test that devices list endpoint requires API key."""
        response = unauthorized_client.get('/devices')
        assert response.status_code == 401

    def test_heartbeat_requires_api_key(self, unauthorized_client):
        """Test that heartbeat endpoint requires API key."""
        response = unauthorized_client.post('/heartbeat',
                                             json={'device_id': 'test-123'},
                                             content_type='application/json')
        assert response.status_code == 401

    def test_invalid_api_key_rejected(self, unauthorized_client):
        """Test that invalid API key is rejected."""
        response = unauthorized_client.post('/chat',
                                             headers={'X-API-Key': 'wrong-key'},
                                             json={'message': 'test'},
                                             content_type='application/json')
        assert response.status_code == 401

    def test_empty_api_key_rejected(self, unauthorized_client):
        """Test that empty API key is rejected."""
        response = unauthorized_client.post('/chat',
                                             headers={'X-API-Key': ''},
                                             json={'message': 'test'},
                                             content_type='application/json')
        assert response.status_code == 401

    def test_options_request_allowed(self, unauthorized_client):
        """Test that OPTIONS requests are allowed (for CORS preflight)."""
        response = unauthorized_client.options('/chat')
        # OPTIONS should not return 401
        assert response.status_code != 401


class TestAPIKeyHeader:
    """Tests for API key header handling."""

    def test_api_key_case_sensitive(self, unauthorized_client):
        """Test that API key comparison is case-sensitive."""
        # Test with wrong case
        response = unauthorized_client.post('/chat',
                                             headers={'X-API-Key': 'TEST-API-KEY-12345'},
                                             json={'message': 'test'},
                                             content_type='application/json')
        assert response.status_code == 401

    def test_api_key_header_name_case_insensitive(self, unauthorized_client):
        """Test that header name is case-insensitive (HTTP standard)."""
        # HTTP headers are case-insensitive, but Flask normalizes them
        response = unauthorized_client.post('/chat',
                                             headers={'x-api-key': 'test-api-key-12345'},
                                             json={'message': 'test'},
                                             content_type='application/json')
        # This should work because Flask normalizes header names
        assert response.status_code == 200
