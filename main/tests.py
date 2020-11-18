from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from main.models import SpatialArea, SpatialContext

User = get_user_model()

class HomePageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test",
                                             password="top_secret",
                                             email="test@example.com")

    def test_anon_user(self):
        client = Client()
        url = reverse("home")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")

    def test_logged_in_user(self):
        client = Client()
        client.login(username="test", password="top_secret")
        url = reverse("home")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign Out")

class ApiTestMixin:
    def setUp(self):
        self.user = User.objects.create_user(username="test",
                                             password="top_secret",
                                             email="test@example.com")
        auth_url = reverse("auth_token")
        c = Client()
        response = c.post(auth_url, {"username": "test", "password": "top_secret"})
        self.token = response.json()["token"]
        self.api_client = Client(Authorization=f"Token: {self.token}")


        
        
