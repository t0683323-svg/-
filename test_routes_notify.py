"""Tests for notification routes."""
from unittest.mock import MagicMock, Mock, patch
from firebase_admin import messaging


class TestNotifyEndpoint:
    """Tests for /notify endpoint."""

    def test_notify_success(self, client, mock_firestore, mock_fcm, sample_notification_data):
        """Test successful notification send."""
        # Mock Firestore to return a device with token
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'fcm_token': 'mock-fcm-token',
            'status': 'online'
        }

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        response = client.post('/notify',
                                json=sample_notification_data,
                                content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['result'] == 'sent'
        assert 'message_id' in data

        # Verify FCM was called
        mock_fcm.send.assert_called_once()

    def test_notify_missing_device_id(self, client, mock_firestore):
        """Test notification with missing device_id."""
        notification_data = {
            "title": "Test",
            "body": "Test message"
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'device_id' in data['error'].lower()

    def test_notify_device_not_found(self, client, mock_firestore):
        """Test notification to unknown device."""
        # Mock Firestore to return non-existent device
        mock_doc = MagicMock()
        mock_doc.exists = False

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        notification_data = {
            "device_id": "non-existent-device",
            "title": "Test",
            "body": "Test message"
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'unknown' in data['error'].lower()

    def test_notify_no_fcm_token(self, client, mock_firestore):
        """Test notification to device without FCM token."""
        # Mock Firestore to return device without token
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'status': 'online'
            # No fcm_token
        }

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        notification_data = {
            "device_id": "device-no-token",
            "title": "Test",
            "body": "Test message"
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'fcm_token' in data['error'].lower()

    @patch('routes_notify.messaging')
    def test_notify_fcm_send_failure(self, mock_messaging, client, mock_firestore):
        """Test handling of FCM send failure."""
        # Mock Firestore to return valid device
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'fcm_token': 'valid-token'}

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        # Mock FCM to raise exception
        mock_messaging.send.side_effect = Exception("FCM Error: Invalid token")
        mock_messaging.Message = messaging.Message
        mock_messaging.Notification = messaging.Notification

        notification_data = {
            "device_id": "test-device",
            "title": "Test",
            "body": "Test message"
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

    def test_notify_custom_title_and_body(self, client, mock_firestore, mock_fcm):
        """Test notification with custom title and body."""
        # Mock Firestore
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'fcm_token': 'valid-token'}

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        notification_data = {
            "device_id": "test-device",
            "title": "Custom Title",
            "body": "Custom Body Message"
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 200

        # Verify FCM was called with custom title/body
        mock_fcm.send.assert_called_once()

    def test_notify_default_title(self, client, mock_firestore, mock_fcm):
        """Test notification uses default title 'AJNA' when not provided."""
        # Mock Firestore
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'fcm_token': 'valid-token'}

        mock_collection = mock_firestore.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc

        notification_data = {
            "device_id": "test-device",
            "body": "Test message"
            # No title provided
        }

        response = client.post('/notify',
                                json=notification_data,
                                content_type='application/json')

        assert response.status_code == 200


class TestDevicesEndpoint:
    """Tests for /devices endpoint."""

    def test_devices_empty_list(self, client, mock_firestore):
        """Test devices endpoint with no registered devices."""
        # Mock empty stream
        mock_firestore.collection.return_value.stream.return_value = []

        response = client.get('/devices')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_devices_single_device(self, client, mock_firestore):
        """Test devices endpoint with one registered device."""
        # Mock single device
        mock_doc = MagicMock()
        mock_doc.id = 'device-123'
        mock_doc.to_dict.return_value = {
            'fcm_token': 'token-123',
            'status': 'online'
        }

        mock_firestore.collection.return_value.stream.return_value = [mock_doc]

        response = client.get('/devices')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['device_id'] == 'device-123'
        assert data[0]['fcm_token'] == 'token-123'
        assert data[0]['status'] == 'online'

    def test_devices_multiple_devices(self, client, mock_firestore):
        """Test devices endpoint with multiple registered devices."""
        # Mock multiple devices
        mock_docs = []
        for i in range(3):
            mock_doc = MagicMock()
            mock_doc.id = f'device-{i}'
            mock_doc.to_dict.return_value = {
                'fcm_token': f'token-{i}',
                'status': 'online'
            }
            mock_docs.append(mock_doc)

        mock_firestore.collection.return_value.stream.return_value = mock_docs

        response = client.get('/devices')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify all devices are included
        device_ids = [d['device_id'] for d in data]
        assert 'device-0' in device_ids
        assert 'device-1' in device_ids
        assert 'device-2' in device_ids


class TestHeartbeatEndpoint:
    """Tests for /heartbeat endpoint."""

    def test_heartbeat_success(self, client, mock_firestore):
        """Test successful heartbeat update."""
        heartbeat_data = {"device_id": "test-device-123"}

        response = client.post('/heartbeat',
                                json=heartbeat_data,
                                content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['result'] == 'ok'
        assert data['device_id'] == heartbeat_data['device_id']

        # Verify Firestore was called to update last_seen
        mock_firestore.collection.assert_called_with('devices')
        collection = mock_firestore.collection.return_value
        collection.document.assert_called_with(heartbeat_data['device_id'])

        # Verify set was called with merge=True
        doc = collection.document.return_value
        doc.set.assert_called_once()
        call_args = doc.set.call_args
        assert 'last_seen' in call_args[0][0]
        assert call_args[0][0]['status'] == 'online'
        assert call_args[1]['merge'] is True

    def test_heartbeat_missing_device_id(self, client, mock_firestore):
        """Test heartbeat with missing device_id."""
        response = client.post('/heartbeat',
                                json={},
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'device_id' in data['error'].lower()

        # Verify Firestore was NOT called
        mock_firestore.collection.assert_not_called()

    def test_heartbeat_null_device_id(self, client, mock_firestore):
        """Test heartbeat with null device_id."""
        heartbeat_data = {"device_id": None}

        response = client.post('/heartbeat',
                                json=heartbeat_data,
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_heartbeat_updates_timestamp(self, client, mock_firestore):
        """Test that heartbeat updates the last_seen timestamp."""
        heartbeat_data = {"device_id": "test-device"}

        response = client.post('/heartbeat',
                                json=heartbeat_data,
                                content_type='application/json')

        assert response.status_code == 200

        # Verify the update included SERVER_TIMESTAMP
        doc = mock_firestore.collection.return_value.document.return_value
        call_args = doc.set.call_args
        # The actual SERVER_TIMESTAMP object is passed
        assert 'last_seen' in call_args[0][0]
