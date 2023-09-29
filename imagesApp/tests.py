from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import mock_open, patch

from .models import UploadedImage, Thumbnail


#
class UserImagesAPIViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_images_api_view(self):
        UploadedImage.objects.create(user=self.user, image='test.jpg', token='testtoken')

        response = self.client.get('/user-images/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomAuthTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()

    def test_custom_auth_token(self):
        response = self.client.post('/api-token-auth/', {'username': 'testuser', 'password': 'testpassword'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)


class ThumbnailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()

    def test_thumbnail_view(self):
        uploaded_image = UploadedImage.objects.create(user=self.user, image='test.jpg', token='testtoken')

        thumbnail = Thumbnail.objects.create(image=uploaded_image, size='200x200', token='testtoken')
        thumbnail_url = f'/thumbnail/{thumbnail.token}/'

        self.client.force_authenticate(user=self.user)

        mock_open_func = mock_open(read_data=b'fake_image_data')
        with patch('builtins.open', mock_open_func):
            response = self.client.get(thumbnail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
