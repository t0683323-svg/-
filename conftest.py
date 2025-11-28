"""Pytest configuration and fixtures for testing."""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import firebase_admin
from firebase_admin import credentials

# Set environment variables for testing
os.environ["FIREBASE_CREDENTIALS"] = "/dev/null"
os.environ["API_KEY"] = "test-api-key-12345"


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_initialization():
    """Mock Firebase initialization globally for all tests."""
    # Mock the Firebase initialization to prevent actual connection
    with patch('firebase_admin.credentials.Certificate') as mock_cert, \
         patch('firebase_admin.initialize_app') as mock_init, \
         patch('firebase_admin.get_app') as mock_get_app:

        # Set up the mock to not raise ValueError (app already exists)
        mock_get_app.return_value = MagicMock()
        yield {
            'cert': mock_cert,
            'init': mock_init,
            'get_app': mock_get_app
        }


@pytest.fixture
def mock_firestore():
    """Mock Firestore client for database operations."""
    # Patch the db object that's already been imported in the modules
    with patch('firebase_init.db') as mock_db, \
         patch('routes_firebase.db', mock_db), \
         patch('routes_notify.db', mock_db):

        # Create mock collection and document references
        mock_collection = MagicMock()
        mock_doc = MagicMock()

        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_collection.stream.return_value = []

        # Mock document operations
        mock_doc.set.return_value = None
        mock_doc.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {}

        yield mock_db


@pytest.fixture
def mock_fcm():
    """Mock Firebase Cloud Messaging for sending notifications."""
    with patch('routes_notify.messaging') as mock_messaging:
        mock_messaging.send.return_value = "mock-message-id-12345"
        yield mock_messaging


@pytest.fixture
def client(mock_firestore):
    """Create Flask test client with mocked Firebase and API key."""
    # Import app here to ensure Firebase mocking is in place
    from app import app

    app.config['TESTING'] = True

    # Create a custom test client class that adds API key to all requests
    class AuthenticatedClient:
        def __init__(self, test_client):
            self.test_client = test_client

        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['X-API-Key'] = 'test-api-key-12345'
            return self.test_client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['X-API-Key'] = 'test-api-key-12345'
            return self.test_client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['X-API-Key'] = 'test-api-key-12345'
            return self.test_client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['X-API-Key'] = 'test-api-key-12345'
            return self.test_client.delete(*args, **kwargs)

    with app.test_client() as test_client:
        yield AuthenticatedClient(test_client)


@pytest.fixture
def unauthorized_client(mock_firestore):
    """Create Flask test client without API key for testing auth."""
    from app import app

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_device_data():
    """Sample device data for testing."""
    return {
        "device_id": "test-device-123",
        "fcm_token": "mock-fcm-token-abc123xyz"
    }


@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing."""
    return {
        "device_id": "test-device-123",
        "title": "Test Notification",
        "body": "This is a test notification message"
    }
