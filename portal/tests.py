from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AuditLog


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

    def test_login_inactive_user_shows_pending_approval_warning(self):
        User.objects.create_user(
            username='pendinguser',
            password='SecretPassword123!',
            is_active=False
        )
        response = self.client.post(reverse('portal:login'), {
            'username': 'pendinguser',
            'password': 'SecretPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your account is pending admin approval')


class PortalLogsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='loguser',
            password='SecretPassword123!',
            is_active=True
        )

    def test_logs_view_requires_login(self):
        response = self.client.get(reverse('portal:logs'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('portal:login'), response.url)

    def test_logs_view_authenticated_user_renders_template(self):
        self.client.login(username='loguser', password='SecretPassword123!')
        AuditLog.objects.create(user='loguser', action='Assigned job #1')
        response = self.client.get(reverse('portal:logs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/logs.html')
        self.assertContains(response, 'Assigned job #1')


class ContextProcessorTests(TestCase):

    def setUp(self):
        from django.test import RequestFactory
        from portal.context_processors import pending_users_count
        self.factory = RequestFactory()
        self.pending_users_count = pending_users_count
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            password='Password123!',
            email='admin@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='reguser',
            password='Password123!'
        )

    def test_pending_users_count_anonymous(self):
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        result = self.pending_users_count(request)
        self.assertEqual(result, {'pending_users_count': 0})

    def test_pending_users_count_regular_user(self):
        request = self.factory.get('/')
        request.user = self.regular_user
        result = self.pending_users_count(request)
        self.assertEqual(result, {'pending_users_count': 0})

    def test_pending_users_count_superuser(self):
        User.objects.create_user(username='pending1', password='pw', is_active=False)
        User.objects.create_user(username='pending2', password='pw', is_active=False)
        request = self.factory.get('/')
        request.user = self.superuser
        result = self.pending_users_count(request)
        self.assertEqual(result, {'pending_users_count': 2})


class PortalRegistrationTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_renders_for_unauthenticated_user(self):
        response = self.client.get(reverse('portal:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/register.html')

    def test_register_authenticated_user_redirects_to_dashboard(self):
        user = User.objects.create_user(username='regauthed', password='Password123!')
        self.client.login(username='regauthed', password='Password123!')
        response = self.client.get(reverse('portal:register'))
        self.assertRedirects(response, reverse('portal:dashboard'))

    def test_register_new_user_creates_inactive_account_and_logs_audit(self):
        response = self.client.post(reverse('portal:register'), {
            'username': 'newrecruit',
            'password1': 'StrongP@ssw0rd!123',
            'password2': 'StrongP@ssw0rd!123',
        })
        self.assertRedirects(response, reverse('portal:login'))
        user = User.objects.get(username='newrecruit')
        self.assertFalse(user.is_active)
        self.assertTrue(AuditLog.objects.filter(user='newrecruit', action__contains='Account registered').exists())




