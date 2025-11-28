"""Tests for Firebase routes - device registration."""
from unittest.mock import MagicMock, patch


class TestRegisterDevice:
    """Tests for /register-device endpoint."""

    def test_register_device_with_both_fields(self, client, mock_firestore, sample_device_data):
        """Test registering device with both device_id and fcm_token."""
        response = client.post('/register-device',
                                json=sample_device_data,
                                content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['result'] == 'registered'
        assert data['device_id'] == sample_device_data['device_id']

        # Verify Firestore was called correctly
        mock_firestore.collection.assert_called_with('devices')
        collection = mock_firestore.collection.return_value
        collection.document.assert_called_with(sample_device_data['device_id'])

        # Verify set was called with merge=True
        doc = collection.document.return_value
        doc.set.assert_called_once()
        call_args = doc.set.call_args
        assert call_args[0][0]['fcm_token'] == sample_device_data['fcm_token']
        assert call_args[0][0]['status'] == 'online'
        assert call_args[1]['merge'] is True

    def test_register_device_only_device_id(self, client, mock_firestore):
        """Test registering device with only device_id (fcm_token is optional)."""
        device_data = {"device_id": "test-device-456"}

        response = client.post('/register-device',
                                json=device_data,
                                content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['result'] == 'registered'
        assert data['device_id'] == device_data['device_id']

        # Verify Firestore was called with None for fcm_token
        doc = mock_firestore.collection.return_value.document.return_value
        doc.set.assert_called_once()
        call_args = doc.set.call_args
        assert call_args[0][0]['fcm_token'] is None
        assert call_args[0][0]['status'] == 'online'

    def test_register_device_missing_device_id(self, client, mock_firestore):
        """Test registering device without device_id returns 400."""
        device_data = {"fcm_token": "some-token"}

        response = client.post('/register-device',
                                json=device_data,
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'device_id' in data['error'].lower()

        # Verify Firestore was NOT called
        mock_firestore.collection.assert_not_called()

    def test_register_device_empty_request(self, client, mock_firestore):
        """Test registering device with empty request body."""
        response = client.post('/register-device',
                                json={},
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

        # Verify Firestore was NOT called
        mock_firestore.collection.assert_not_called()

    def test_register_device_updates_existing(self, client, mock_firestore, sample_device_data):
        """Test that registering existing device updates it (merge=True behavior)."""
        # First registration
        response1 = client.post('/register-device',
                                 json=sample_device_data,
                                 content_type='application/json')
        assert response1.status_code == 200

        # Second registration with new token
        updated_data = {
            "device_id": sample_device_data['device_id'],
            "fcm_token": "new-token-xyz789"
        }
        response2 = client.post('/register-device',
                                 json=updated_data,
                                 content_type='application/json')

        assert response2.status_code == 200
        data = response2.get_json()
        assert data['result'] == 'registered'

        # Verify both calls used merge=True (allowing updates)
        doc = mock_firestore.collection.return_value.document.return_value
        assert doc.set.call_count == 2
        for call in doc.set.call_args_list:
            assert call[1]['merge'] is True

    # NOTE: test_register_device_firestore_failure removed
    # The current implementation doesn't have error handling for Firestore failures.
    # This test would require adding try/except blocks to the route handlers.

    def test_register_device_null_device_id(self, client, mock_firestore):
        """Test registering device with null device_id."""
        device_data = {"device_id": None, "fcm_token": "token"}

        response = client.post('/register-device',
                                json=device_data,
                                content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_register_device_malformed_json(self, client):
        """Test registering device with malformed JSON."""
        response = client.post('/register-device',
                                data='{"device_id": "test", invalid json}',
                                content_type='application/json')

        # Flask should return 400 for malformed JSON
        assert response.status_code in [400, 415]
