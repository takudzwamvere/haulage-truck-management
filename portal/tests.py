from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class PortalRedirectTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            is_active=True
        )

    def test_root_redirect_unauthenticated_user(self):
        response = self.client.get(reverse('portal:root'))
        self.assertRedirects(response, reverse('portal:login'))

    def test_root_redirect_authenticated_user(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('portal:root'))
        self.assertRedirects(response, reverse('portal:dashboard'))
