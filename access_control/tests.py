from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import AccessLog
import os


class AccessLogModelTest(TestCase):
    """Unit tests for the AccessLog model."""
    
    def setUp(self):
        """Create required data before each test."""
        self.access_log = AccessLog.objects.create(
            card_id='C1001',
            door_name='Main Entrance',
            access_granted=True
        )
    
    def test_access_log_creation(self):
        """Test whether the AccessLog object is created correctly."""
        self.assertEqual(self.access_log.card_id, 'C1001')
        self.assertEqual(self.access_log.door_name, 'Main Entrance')
        self.assertTrue(self.access_log.access_granted)
    
    def test_access_log_string_representation(self):
        """Test whether the __str__ method of AccessLog works correctly."""
        expected_str = f"C1001 - Main Entrance (GRANTED) at {self.access_log.timestamp}"
        self.assertEqual(str(self.access_log), expected_str)
    
    def test_timestamp_auto_set(self):
        """Test whether the timestamp is set automatically."""
        self.assertIsNotNone(self.access_log.timestamp)
    
    def test_denied_access_log(self):
        """Create and test a denied access log."""
        denied_log = AccessLog.objects.create(
            card_id='C1002',
            door_name='Secure Room',
            access_granted=False
        )
        self.assertFalse(denied_log.access_granted)


class AccessLogAPITest(TestCase):
    """Unit tests for AccessLog API endpoints."""
    
    def setUp(self):
        """Setup before each test."""
        self.client = APIClient()
        self.list_url = reverse('accesslog-list')
        
        # Create test data
        self.access_log1 = AccessLog.objects.create(
            card_id='C1001',
            door_name='Main Entrance',
            access_granted=True
        )
        self.access_log2 = AccessLog.objects.create(
            card_id='C1002',
            door_name='Back Door',
            access_granted=False
        )
        self.detail_url = reverse('accesslog-detail', kwargs={'pk': self.access_log1.pk})
    
    def test_create_access_log(self):
        """Test whether a new AccessLog can be created."""
        data = {
            'card_id': 'C1003',
            'door_name': 'Lab Room',
            'access_granted': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AccessLog.objects.count(), 3)
    
    def test_create_access_log_missing_field(self):
        """Test whether creation fails when a required field is missing."""
        data = {
            'card_id': 'C1003',
            # door_name field is missing
            'access_granted': True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_access_logs(self):
        """Test whether all AccessLogs can be retrieved."""
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_access_log(self):
        """Test whether a specific AccessLog can be retrieved."""
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['card_id'], 'C1001')
    
    def test_update_access_log(self):
        """Test whether an AccessLog can be updated."""
        data = {
            'card_id': 'C1001',
            'door_name': 'Main Entrance Updated',
            'access_granted': False
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_log1.refresh_from_db()
        self.assertEqual(self.access_log1.door_name, 'Main Entrance Updated')
    
    def test_delete_access_log(self):
        """Test whether an AccessLog can be deleted."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessLog.objects.count(), 1)
    
    def test_filter_by_card_id(self):
        """Test whether filtering by card_id works."""
        response = self.client.get(self.list_url, {'card_id': 'C1001'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['card_id'], 'C1001')
    
    def test_filter_by_access_granted(self):
        """Test whether filtering by access_granted works."""
        response = self.client.get(self.list_url, {'access_granted': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertFalse(response.data['results'][0]['access_granted'])
    
    def test_stats_endpoint(self):
        """Test whether the stats endpoint works correctly."""
        stats_url = reverse('accesslog-stats')
        response = self.client.get(stats_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_logs'], 2)
        self.assertEqual(response.data['granted_access'], 1)
        self.assertEqual(response.data['denied_access'], 1)
    
    def test_denied_access_endpoint(self):
        """Test whether the denied access endpoint works correctly."""
        denied_url = reverse('accesslog-denied-access')
        response = self.client.get(denied_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['access_granted'])
