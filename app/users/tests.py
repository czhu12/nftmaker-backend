from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):
    def test_create_new_user(self):
        response = self.client.post(
            reverse('auth_register'),
            {
                'username': 'chris',
                'email': 'chris@example.com',
                'password': 'SecretPassword!',
                'password_confirmation': 'SecretPassword!'
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue('token' in response.json())

    def test_get_auth_token(self):
        # First create the user
        self.client.post(
            reverse('auth_register'),
            {
                'username': 'chris',
                'email': 'chris@example.com',
                'password': 'SecretPassword!',
                'password_confirmation': 'SecretPassword!'
            },
        )

        response = self.client.post(
            reverse('api_token_auth'),
            {
                'username': 'chris',
                'password': 'SecretPassword!',
            },
        )
        self.assertTrue('token' in response.json())
