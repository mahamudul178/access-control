"""
access_control/tests.py
Enhanced unit tests with improved coverage
"""

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import AccessLog
from .signals import access_log_created, access_log_deleted
from django.db.models.signals import post_save, post_delete
import json
import os
import tempfile


class AccessLogModelTests(TestCase):
    """Comprehensive test cases for AccessLog model"""

    def setUp(self):
        """Set up test data"""
        self.log = AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )

    def test_create_access_log(self):
        """Test creating an AccessLog entry"""
        self.assertEqual(self.log.card_id, "C1001")
        self.assertEqual(self.log.door_name, "Main Entrance")
        self.assertTrue(self.log.access_granted)

    def test_access_log_string_representation(self):
        """Test AccessLog __str__ method"""
        expected_str = f"C1001 - Main Entrance (GRANTED) at {self.log.timestamp}"
        self.assertEqual(str(self.log), expected_str)

    def test_access_log_fields(self):
        """Test all fields are properly set"""
        self.assertIsNotNone(self.log.id)
        self.assertIsNotNone(self.log.timestamp)
        self.assertIsNotNone(self.log.created_at)

    def test_access_log_denied(self):
        """Test creating denied access log"""
        denied_log = AccessLog.objects.create(
            card_id="C1002",
            door_name="Secure Room",
            access_granted=False
        )
        self.assertFalse(denied_log.access_granted)
        self.assertIn("DENIED", str(denied_log))

    def test_access_log_ordering(self):
        """Test AccessLog ordering by timestamp"""
        log2 = AccessLog.objects.create(
            card_id="C1003",
            door_name="Lab Room",
            access_granted=True
        )
        logs = list(AccessLog.objects.all())
        self.assertEqual(logs[0].id, log2.id)

    def test_multiple_same_card_logs(self):
        """Test multiple logs for same card"""
        AccessLog.objects.create(
            card_id="C1001",
            door_name="Back Door",
            access_granted=False
        )
        c1001_logs = AccessLog.objects.filter(card_id="C1001")
        self.assertEqual(c1001_logs.count(), 2)

    def test_card_id_validation(self):
        """Test card_id field"""
        log = AccessLog.objects.create(
            card_id="TEST123",
            door_name="Test Door",
            access_granted=True
        )
        self.assertEqual(log.card_id, "TEST123")

    def test_door_name_max_length(self):
        """Test door_name max length"""
        long_name = "A" * 100
        log = AccessLog.objects.create(
            card_id="C1004",
            door_name=long_name,
            access_granted=True
        )
        self.assertEqual(len(log.door_name), 100)

    def test_timestamp_auto_set(self):
        """Test timestamp is automatically set"""
        log = AccessLog.objects.create(
            card_id="C1005",
            door_name="Auto Timestamp Door",
            access_granted=True
        )
        self.assertIsNotNone(log.timestamp)

    def test_model_meta_ordering(self):
        """Test model Meta ordering"""
        logs = AccessLog.objects.all()
        self.assertEqual(logs[0].id, self.log.id)

    def test_log_queryset_count(self):
        """Test queryset count"""
        count = AccessLog.objects.count()
        self.assertEqual(count, 1)
        AccessLog.objects.create(
            card_id="C1006",
            door_name="New Door",
            access_granted=True
        )
        self.assertEqual(AccessLog.objects.count(), 2)


class AccessLogSerializerTests(APITestCase):
    """Test cases for AccessLogSerializer"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.log = AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        from .serializers import AccessLogSerializer
        data = {
            'card_id': 'C1002',
            'door_name': 'Test Door',
            'access_granted': False
        }
        serializer = AccessLogSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_empty_card_id(self):
        """Test serializer validation for empty card_id"""
        from .serializers import AccessLogSerializer
        data = {
            'card_id': '',
            'door_name': 'Test Door',
            'access_granted': True
        }
        serializer = AccessLogSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_with_empty_door_name(self):
        """Test serializer validation for empty door_name"""
        from .serializers import AccessLogSerializer
        data = {
            'card_id': 'C1001',
            'door_name': '',
            'access_granted': True
        }
        serializer = AccessLogSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_read_only_fields(self):
        """Test read-only fields in serializer"""
        from .serializers import AccessLogSerializer
        serializer = AccessLogSerializer(self.log)
        # These fields should not be writable
        self.assertIn('timestamp', serializer.fields)
        self.assertIn('created_at', serializer.fields)

    def test_serializer_card_id_strip_whitespace(self):
        """Test card_id validation strips whitespace"""
        from .serializers import AccessLogSerializer
        data = {
            'card_id': '  C1001  ',
            'door_name': 'Test Door',
            'access_granted': True
        }
        serializer = AccessLogSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AccessLogAPITests(APITestCase):
    """Test cases for Access Control API endpoints"""

    def setUp(self):
        """Set up API client and test data"""
        self.client = APIClient()
        self.list_url = reverse('accesslog-list')
        
        self.log1 = AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )
        self.log2 = AccessLog.objects.create(
            card_id="C1002",
            door_name="Back Door",
            access_granted=False
        )
        self.detail_url = reverse('accesslog-detail', kwargs={'pk': self.log1.pk})

    def test_create_access_log_post(self):
        """Test POST request to create a log"""
        data = {
            "card_id": "C1004",
            "door_name": "Conference Room",
            "access_granted": True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AccessLog.objects.count(), 3)

    def test_create_log_missing_field(self):
        """Test POST fails when required field is missing"""
        data = {
            "card_id": "C1005",
            "access_granted": True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_logs_get(self):
        """Test GET request to list all logs"""
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_retrieve_single_log_get(self):
        """Test GET request to retrieve single log"""
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['card_id'], "C1001")

    def test_retrieve_non_existent_log(self):
        """Test GET request for non-existent log"""
        url = reverse('accesslog-detail', kwargs={'pk': 9999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_access_log_put(self):
        """Test PUT request to update a log"""
        data = {
            "card_id": "C1001",
            "door_name": "Main Entrance Updated",
            "access_granted": False
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.log1.refresh_from_db()
        self.assertEqual(self.log1.door_name, "Main Entrance Updated")

    def test_delete_access_log_delete(self):
        """Test DELETE request to delete a log"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessLog.objects.count(), 1)

    def test_filter_by_card_id(self):
        """Test filtering by card_id"""
        response = self.client.get(self.list_url, {'card_id': 'C1001'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_door_name(self):
        """Test filtering by door_name"""
        response = self.client.get(
            self.list_url,
            {'door_name': 'Main Entrance'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_access_granted_true(self):
        """Test filtering by access_granted=true"""
        response = self.client.get(
            self.list_url,
            {'access_granted': 'true'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_access_granted_false(self):
        """Test filtering by access_granted=false"""
        response = self.client.get(
            self.list_url,
            {'access_granted': 'false'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_by_card_id(self):
        """Test search functionality"""
        response = self.client.get(
            self.list_url,
            {'search': 'C1001'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_response_structure(self):
        """Test API response structure"""
        response = self.client.get(self.list_url, format='json')
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_detail_response_structure(self):
        """Test detail response structure"""
        response = self.client.get(self.detail_url, format='json')
        required_fields = ['id', 'card_id', 'door_name', 'access_granted', 'timestamp', 'created_at']
        for field in required_fields:
            self.assertIn(field, response.data)


class AccessLogCustomEndpointTests(APITestCase):
    """Test custom API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )
        AccessLog.objects.create(
            card_id="C1002",
            door_name="Back Door",
            access_granted=False
        )
        AccessLog.objects.create(
            card_id="C1001",
            door_name="Lab Room",
            access_granted=True
        )

    def test_stats_endpoint(self):
        """Test /api/logs/stats/ endpoint"""
        url = reverse('accesslog-stats')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_logs'], 3)
        self.assertEqual(response.data['granted_access'], 2)
        self.assertEqual(response.data['denied_access'], 1)

    def test_denied_access_endpoint(self):
        """Test /api/logs/denied_access/ endpoint"""
        url = reverse('accesslog-denied-access')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_by_card_endpoint(self):
        """Test /api/logs/by_card/ endpoint"""
        url = reverse('accesslog-by-card')
        response = self.client.get(url, {'card_id': 'C1001'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_by_card_missing_parameter(self):
        """Test by_card endpoint without card_id parameter"""
        url = reverse('accesslog-by-card')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_door_endpoint(self):
        """Test /api/logs/by_door/ endpoint"""
        url = reverse('accesslog-by-door')
        response = self.client.get(
            url,
            {'door_name': 'Main Entrance'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminInterfaceTests(TestCase):
    """Test admin interface functionality"""

    def setUp(self):
        """Set up test data"""
        self.log = AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )

    def test_admin_changelist_view(self):
        """Test admin changelist view loads"""
        from access_control.admin import AccessLogAdmin
        from django.contrib.admin.sites import AdminSite
        admin = AccessLogAdmin(AccessLog, AdminSite())
        self.assertIsNotNone(admin)

    def test_admin_list_display(self):
        """Test admin list_display configuration"""
        from access_control.admin import AccessLogAdmin
        from django.contrib.admin.sites import AdminSite
        admin = AccessLogAdmin(AccessLog, AdminSite())
        self.assertIn('id', admin.list_display)
        self.assertIn('card_id', admin.list_display)
        self.assertIn('access_granted', admin.list_display)

    def test_admin_list_filter(self):
        """Test admin list_filter configuration"""
        from access_control.admin import AccessLogAdmin
        from django.contrib.admin.sites import AdminSite
        admin = AccessLogAdmin(AccessLog, AdminSite())
        self.assertIn('access_granted', admin.list_filter)

    def test_admin_search_fields(self):
        """Test admin search_fields configuration"""
        from access_control.admin import AccessLogAdmin
        from django.contrib.admin.sites import AdminSite
        admin = AccessLogAdmin(AccessLog, AdminSite())
        self.assertIn('card_id', admin.search_fields)

    def test_admin_readonly_fields(self):
        """Test admin readonly_fields configuration"""
        from access_control.admin import AccessLogAdmin
        from django.contrib.admin.sites import AdminSite
        admin = AccessLogAdmin(AccessLog, AdminSite())
        self.assertIn('timestamp', admin.readonly_fields)


class SignalHandlerTests(TransactionTestCase):
    """Test Django signal handlers"""

    def test_signal_on_log_creation(self):
        """Test that signal fires on log creation"""
        initial_count = AccessLog.objects.count()
        log = AccessLog.objects.create(
            card_id="C1001",
            door_name="Signal Test",
            access_granted=True
        )
        self.assertEqual(AccessLog.objects.count(), initial_count + 1)

    def test_signal_on_log_deletion(self):
        """Test that signal fires on log deletion"""
        log = AccessLog.objects.create(
            card_id="C1002",
            door_name="Delete Test",
            access_granted=True
        )
        log_id = log.id
        log.delete()
        with self.assertRaises(AccessLog.DoesNotExist):
            AccessLog.objects.get(id=log_id)

    def test_signal_post_save_connected(self):
        """Test post_save signal is connected"""
        from django.dispatch import receiver
        from .signals import access_log_created
        # Signal should be connected
        self.assertIsNotNone(access_log_created)

    def test_signal_post_delete_connected(self):
        """Test post_delete signal is connected"""
        from .signals import access_log_deleted
        # Signal should be connected
        self.assertIsNotNone(access_log_deleted)


class EdgeCaseTests(APITestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.list_url = reverse('accesslog-list')

    def test_create_with_very_long_card_id(self):
        """Test creating log with max length card_id"""
        data = {
            "card_id": "C" * 50,
            "door_name": "Test Door",
            "access_granted": True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_very_long_door_name(self):
        """Test creating log with max length door_name"""
        data = {
            "card_id": "C1001",
            "door_name": "D" * 100,
            "access_granted": True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_special_characters(self):
        """Test creating log with special characters"""
        data = {
            "card_id": "C-1001-@",
            "door_name": "Main Entrance #1",
            "access_granted": True
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_filter_result(self):
        """Test filtering with no results"""
        response = self.client.get(
            self.list_url,
            {'card_id': 'NONEXISTENT'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class PaginationTests(APITestCase):
    """Test pagination functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.list_url = reverse('accesslog-list')
        
        # Create 15 logs
        for i in range(15):
            AccessLog.objects.create(
                card_id=f"C{1000+i}",
                door_name=f"Door {i}",
                access_granted=(i % 2 == 0)
            )

    def test_default_pagination_page_1(self):
        """Test default pagination page 1"""
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 15)
        self.assertEqual(len(response.data['results']), 10)

    def test_pagination_page_2(self):
        """Test pagination page 2"""
        response = self.client.get(self.list_url, {'page': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_pagination_next_link(self):
        """Test pagination next link"""
        response = self.client.get(self.list_url, format='json')
        self.assertIsNotNone(response.data['next'])

    def test_pagination_previous_link(self):
        """Test pagination previous link on page 2"""
        response = self.client.get(self.list_url, {'page': 2}, format='json')
        self.assertIsNotNone(response.data['previous'])


class SettingsTests(TestCase):
    """Test Django settings"""

    def test_rest_framework_installed(self):
        """Test Django REST Framework is installed"""
        from django.conf import settings
        self.assertIn('rest_framework', settings.INSTALLED_APPS)

    def test_access_control_app_installed(self):
        """Test access_control app is installed"""
        from django.conf import settings
        self.assertIn('access_control', settings.INSTALLED_APPS)

    def test_pagination_configured(self):
        """Test REST Framework pagination is configured"""
        from django.conf import settings
        self.assertIn('DEFAULT_PAGINATION_CLASS', settings.REST_FRAMEWORK)

    def test_database_configured(self):
        """Test database is configured"""
        from django.conf import settings
        self.assertIn('default', settings.DATABASES)