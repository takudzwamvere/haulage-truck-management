from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Truck, Driver, Job, AuditLog


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


class PortalUserApprovalTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword123!',
            email='admin@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='UserPassword123!',
            is_active=True
        )
        self.pending_user = User.objects.create_user(
            username='applicant',
            password='PendingPassword123!',
            is_active=False
        )

    def test_pending_users_view_forbidden_for_regular_user(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.get(reverse('portal:pending_users'))
        self.assertRedirects(response, reverse('portal:dashboard'))

    def test_pending_users_view_accessible_by_superuser(self):
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.get(reverse('portal:pending_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/pending_users.html')
        self.assertContains(response, 'applicant')

    def test_approve_user_activates_user(self):
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('portal:approve_user', args=[self.pending_user.pk]))
        self.assertRedirects(response, reverse('portal:pending_users'))
        self.pending_user.refresh_from_db()
        self.assertTrue(self.pending_user.is_active)
        self.assertTrue(AuditLog.objects.filter(action__contains='Approved user applicant').exists())

    def test_reject_user_deletes_user(self):
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('portal:reject_user', args=[self.pending_user.pk]))
        self.assertRedirects(response, reverse('portal:pending_users'))
        self.assertFalse(User.objects.filter(pk=self.pending_user.pk).exists())
        self.assertTrue(AuditLog.objects.filter(action__contains='Rejected and deleted user applicant').exists())


class PortalDashboardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashuser',
            password='DashPassword123!',
            is_active=True
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('portal:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('portal:login'), response.url)

    def test_dashboard_renders_with_correct_metrics(self):
        self.client.login(username='dashuser', password='DashPassword123!')

        Truck.objects.create(registration_no='TRK-01', capacity=10, status='available')
        Truck.objects.create(registration_no='TRK-02', capacity=20, status='in_transit')
        Driver.objects.create(name='Driver One', license_no='LIC-01', phone_no='12345678')
        Job.objects.create(
            pick_up_location='City A',
            delivery_location='City B',
            cargo='Machinery',
            status='pending'
        )

        response = self.client.get(reverse('portal:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/dashboard.html')
        self.assertEqual(response.context['total_trucks'], 2)
        self.assertEqual(response.context['available_trucks'], 1)
        self.assertEqual(response.context['in_transit_trucks'], 1)
        self.assertEqual(response.context['total_drivers'], 1)
        self.assertEqual(response.context['total_jobs'], 1)
        self.assertEqual(response.context['pending_jobs'], 1)


class PortalTruckViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword123!',
            email='admin@example.com'
        )
        self.user = User.objects.create_user(
            username='regularuser',
            password='UserPassword123!',
            is_active=True
        )
        self.truck = Truck.objects.create(
            registration_no='ZW-100',
            capacity=25.5,
            status='available'
        )

    def test_truck_list_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.get(reverse('portal:truck_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/trucks/list.html')
        self.assertContains(response, 'ZW-100')

    def test_truck_create_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:truck_create'), {
            'registration_no': 'ZW-200',
            'capacity': '30.0',
            'status': 'available',
        })
        self.assertRedirects(response, reverse('portal:truck_list'))
        self.assertTrue(Truck.objects.filter(registration_no='ZW-200').exists())
        self.assertTrue(AuditLog.objects.filter(action__contains='Created truck ZW-200').exists())

    def test_truck_edit_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:truck_edit', args=[self.truck.pk]), {
            'registration_no': 'ZW-100',
            'capacity': '35.0',
            'status': 'maintenance',
        })
        self.assertRedirects(response, reverse('portal:truck_list'))
        self.truck.refresh_from_db()
        self.assertEqual(self.truck.status, 'maintenance')

    def test_truck_delete_non_superuser_forbidden(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:truck_delete', args=[self.truck.pk]))
        self.assertRedirects(response, reverse('portal:truck_list'))
        self.assertTrue(Truck.objects.filter(pk=self.truck.pk).exists())

    def test_truck_delete_superuser_success(self):
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('portal:truck_delete', args=[self.truck.pk]))
        self.assertRedirects(response, reverse('portal:truck_list'))
        self.assertFalse(Truck.objects.filter(pk=self.truck.pk).exists())


class PortalDriverViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword123!',
            email='admin@example.com'
        )
        self.user = User.objects.create_user(
            username='regularuser',
            password='UserPassword123!',
            is_active=True
        )
        self.driver = Driver.objects.create(
            name='Kudzi Shumba',
            license_no='ZW-DL-999',
            phone_no='0778889999'
        )

    def test_driver_list_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.get(reverse('portal:driver_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/drivers/list.html')
        self.assertContains(response, 'Kudzi Shumba')

    def test_driver_create_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:driver_create'), {
            'name': 'Tatenda Biti',
            'license_no': 'ZW-DL-777',
            'phone_no': '0771112222',
        })
        self.assertRedirects(response, reverse('portal:driver_list'))
        self.assertTrue(Driver.objects.filter(license_no='ZW-DL-777').exists())
        self.assertTrue(AuditLog.objects.filter(action__contains='Created driver Tatenda Biti').exists())

    def test_driver_edit_view(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:driver_edit', args=[self.driver.pk]), {
            'name': 'Kudzi Shumba Updated',
            'license_no': 'ZW-DL-999',
            'phone_no': '0779990000',
        })
        self.assertRedirects(response, reverse('portal:driver_list'))
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.name, 'Kudzi Shumba Updated')

    def test_driver_delete_non_superuser_forbidden(self):
        self.client.login(username='regularuser', password='UserPassword123!')
        response = self.client.post(reverse('portal:driver_delete', args=[self.driver.pk]))
        self.assertRedirects(response, reverse('portal:driver_list'))
        self.assertTrue(Driver.objects.filter(pk=self.driver.pk).exists())

    def test_driver_delete_superuser_success(self):
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('portal:driver_delete', args=[self.driver.pk]))
        self.assertRedirects(response, reverse('portal:driver_list'))
        self.assertFalse(Driver.objects.filter(pk=self.driver.pk).exists())








