"""Tests for core app.py endpoints."""
import json
from unittest.mock import patch, Mock
import requests


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint_returns_ok(self, client):
        """Test that health endpoint returns status ok."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'time' in data

    def test_health_endpoint_returns_iso8601_timestamp(self, client):
        """Test that health endpoint returns ISO 8601 timestamp."""
        response = client.get('/health')
        data = response.get_json()
        # Verify timestamp format (should contain 'T' and timezone info)
        assert 'T' in data['time']
        assert '+' in data['time'] or 'Z' in data['time']


class TestChatEndpoint:
    """Tests for /chat endpoint."""

    def test_chat_valid_message(self, client):
        """Test chat endpoint with valid message."""
        response = client.post('/chat',
                                json={'message': 'Hello, World!'},
                                content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == 'Echo: Hello, World!'

    def test_chat_missing_message_field(self, client):
        """Test chat endpoint with missing message field."""
        response = client.post('/chat',
                                json={},
                                content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['error'].lower()

    def test_chat_empty_message(self, client):
        """Test chat endpoint with empty message string."""
        response = client.post('/chat',
                                json={'message': ''},
                                content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_chat_with_special_characters(self, client):
        """Test chat endpoint with special characters in message."""
        special_msg = "Test <script>alert('XSS')</script> & symbols!"
        response = client.post('/chat',
                                json={'message': special_msg},
                                content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == f'Echo: {special_msg}'


class TestLLMEndpoint:
    """Tests for /llm endpoint."""

    def test_llm_missing_message_field(self, client):
        """Test LLM endpoint with missing message field."""
        response = client.post('/llm',
                                json={},
                                content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['error'].lower()

    def test_llm_empty_message(self, client):
        """Test LLM endpoint with empty message string."""
        response = client.post('/llm',
                                json={'message': ''},
                                content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @patch('app.requests.post')
    def test_llm_valid_request(self, mock_post, client):
        """Test LLM endpoint with valid request and mocked service."""
        # Mock successful LLM service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"response": "This is a generated response"}'
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        response = client.post('/llm',
                                json={'message': 'Tell me a joke'},
                                content_type='application/json')

        assert response.status_code == 200
        assert mock_post.called
        # Verify the LLM service was called with correct parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == 'http://127.0.0.1:11434/api/generate'
        assert call_args[1]['json']['model'] == 'llama3.2:3b'
        assert call_args[1]['json']['prompt'] == 'Tell me a joke'
        assert call_args[1]['timeout'] == 30

    @patch('app.requests.post')
    def test_llm_service_unavailable(self, mock_post, client):
        """Test LLM endpoint when service is unavailable."""
        # Mock service connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Service unavailable")

        response = client.post('/llm',
                                json={'message': 'Test message'},
                                content_type='application/json')

        assert response.status_code == 503
        data = response.get_json()
        assert 'error' in data
        assert 'unavailable' in data['error'].lower()

    @patch('app.requests.post')
    def test_llm_timeout(self, mock_post, client):
        """Test LLM endpoint timeout handling."""
        # Mock timeout error
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        response = client.post('/llm',
                                json={'message': 'Test message'},
                                content_type='application/json')

        assert response.status_code == 503
        data = response.get_json()
        assert 'error' in data
        assert 'unavailable' in data['error'].lower()

    @patch('app.requests.post')
    def test_llm_empty_response(self, mock_post, client):
        """Test LLM endpoint with empty response from service."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        response = client.post('/llm',
                                json={'message': 'Test message'},
                                content_type='application/json')

        assert response.status_code == 502
        data = response.get_json()
        assert 'error' in data
        assert 'empty' in data['error'].lower()

    @patch('app.requests.post')
    def test_llm_http_error(self, mock_post, client):
        """Test LLM endpoint with HTTP error from service."""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response

        response = client.post('/llm',
                                json={'message': 'Test message'},
                                content_type='application/json')

        assert response.status_code == 503
        data = response.get_json()
        assert 'error' in data
