from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Activity, ActivityCategory


class ActivityCategoryFilterTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reader@example.com',
            password='StrongPass123!',
            name='Reader',
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = '/api/activities/'

        self.breathing_activity = Activity.objects.create(
            name='Box Breathing',
            description='A calming breathing exercise.',
            category=ActivityCategory.BREATHING,
            time_takes=5,
            emoji='B',
            steps=['Inhale', 'Hold', 'Exhale'],
        )
        Activity.objects.create(
            name='Body Scan',
            description='A guided meditation.',
            category=ActivityCategory.MEDITATION,
            time_takes=10,
            emoji='M',
            steps=['Relax', 'Scan body', 'Breathe'],
        )

    def test_list_filters_by_unquoted_category_param(self):
        response = self.client.get(self.list_url, {'category': 'breathing'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.breathing_activity.id))
        self.assertEqual(response.data[0]['category'], ActivityCategory.BREATHING)

    def test_list_filters_by_quoted_category_param(self):
        response = self.client.get(self.list_url, {'category': '"breathing"'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.breathing_activity.id))
        self.assertEqual(response.data[0]['category'], ActivityCategory.BREATHING)

    def test_list_rejects_invalid_category_param(self):
        response = self.client.get(self.list_url, {'category': 'invalid'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['category'], 'Invalid category.')
