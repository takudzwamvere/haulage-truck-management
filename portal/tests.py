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


class PortalAuthTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='portaluser',
            password='SecretPassword123!',
            is_active=True
        )

    def test_login_page_renders_successfully(self):
        response = self.client.get(reverse('portal:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/login.html')

    def test_login_authenticated_user_redirects_to_dashboard(self):
        self.client.login(username='portaluser', password='SecretPassword123!')
        response = self.client.get(reverse('portal:login'))
        self.assertRedirects(response, reverse('portal:dashboard'))

    def test_login_success(self):
        response = self.client.post(reverse('portal:login'), {
            'username': 'portaluser',
            'password': 'SecretPassword123!',
        })
        self.assertRedirects(response, reverse('portal:dashboard'))

    def test_login_invalid_credentials_shows_error(self):
        response = self.client.post(reverse('portal:login'), {
            'username': 'portaluser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
