from django.test import TestCase
from django.core.exceptions import ValidationError
from jose import jwt
from core.models import Truck, Driver, Job, AuditLog
from core.auth import create_access_token, decode_access_token, SECRET_KEY, ALGORITHM


class BusinessRuleTest(TestCase):

    def setUp(self):
        self.truck = Truck.objects.create(
            registration_no='ZW1234',
            capacity=5000,
            status='available'
        )
        self.driver = Driver.objects.create(
            name='John Doe',
            license_no='DL12345',
            phone_no='0771234567'
        )
        self.job = Job.objects.create(
            pick_up_location='Harare',
            delivery_location='Bulawayo',
            cargo='Electronics',
            status='pending'
        )

    def test_truck_str_representation(self):
        self.assertEqual(str(self.truck), 'ZW1234 - available')

    def test_driver_str_representation(self):
        self.assertEqual(str(self.driver), 'John Doe: DL12345')

    def test_job_str_representation(self):
        self.assertEqual(str(self.job), f'Job {self.job.id} (pending)')

    def test_audit_log_str_representation(self):
        log = AuditLog.objects.create(user='admin', action='Created driver John Doe')
        self.assertIn('admin: Created driver John Doe', str(log))

    def test_truck_in_transit_cannot_be_assigned(self):
        self.assertIn(self.truck, Truck.objects.filter(status='available'))
        self.truck.status = 'in_transit'
        self.truck.save()
        self.assertNotIn(self.truck, Truck.objects.filter(status='available'))

    def test_truck_in_maintenance_cannot_be_assigned(self):
        self.assertIn(self.truck, Truck.objects.filter(status='available'))
        self.truck.status = 'maintenance'
        self.truck.save()
        self.assertNotIn(self.truck, Truck.objects.filter(status='available'))

    def test_completing_job_frees_truck(self):
        self.truck.status = 'in_transit'
        self.truck.save()
        self.assertNotIn(self.truck, Truck.objects.filter(status='available'))
        self.truck.status = 'available'
        self.truck.save()
        self.assertIn(self.truck, Truck.objects.filter(status='available'))

    def test_cancelling_job_frees_truck(self):
        self.truck.status = 'in_transit'
        self.truck.save()
        self.assertNotIn(self.truck, Truck.objects.filter(status='available'))
        self.truck.status = 'available'
        self.truck.save()
        self.assertIn(self.truck, Truck.objects.filter(status='available'))

    def test_driver_cannot_have_two_active_jobs(self):
        active_jobs = Job.objects.filter(
            assigned_driver=self.driver,
            status__in=['pending', 'in_transit']
        )
        self.assertFalse(active_jobs.exists())
        self.job.assigned_driver = self.driver
        self.job.status = 'in_transit'
        self.job.save()
        active_jobs = Job.objects.filter(
            assigned_driver=self.driver,
            status__in=['pending', 'in_transit']
        )
        self.assertTrue(active_jobs.exists())

    def test_same_pickup_and_delivery_location_raises_validation_error(self):
        job = Job(
            pick_up_location='Harare',
            delivery_location=' harare ',
            cargo='Electronics',
            status='pending',
        )
        with self.assertRaises(ValidationError) as ctx:
            job.full_clean()
        self.assertIn('delivery_location', ctx.exception.message_dict)

    def test_invalid_status_transition_raises_validation_error(self):
        self.job.status = 'in_transit'
        self.job.save()
        self.job.status = 'completed'
        self.job.save()

        self.job.status = 'pending'
        with self.assertRaises(ValidationError) as ctx:
            self.job.full_clean()
        self.assertIn('status', ctx.exception.message_dict)


class AuthTokenTest(TestCase):

    def test_create_and_decode_token_success(self):
        token = create_access_token(user_id=42)
        decoded_id = decode_access_token(token)
        self.assertEqual(decoded_id, 42)

    def test_decode_invalid_token_returns_none(self):
        self.assertIsNone(decode_access_token('invalid-garbage-token'))

    def test_decode_token_with_non_integer_sub_returns_none(self):
        token = jwt.encode({'sub': 'not-an-int'}, SECRET_KEY, algorithm=ALGORITHM)
        self.assertIsNone(decode_access_token(token))


class ApiAuthEndpointTests(TestCase):

    def setUp(self):
        import json
        from django.contrib.auth.models import User
        from django.test import Client
        self.client = Client()
        self.json = json
        self.user = User.objects.create_user(
            username='apitester',
            password='SecretPassword123!',
            is_active=True
        )

    def test_login_endpoint_success(self):
        response = self.client.post(
            '/api/auth/login/',
            data=self.json.dumps({'username': 'apitester', 'password': 'SecretPassword123!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access_token', data)
        self.assertEqual(data.get('token_type'), 'bearer')
        self.assertEqual(decode_access_token(data['access_token']), self.user.id)

    def test_login_endpoint_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            data=self.json.dumps({'username': 'apitester', 'password': 'WrongPassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'Invalid username or password')


class ApiTruckEndpointTests(TestCase):

    def setUp(self):
        import json
        from django.contrib.auth.models import User
        from django.test import Client
        self.client = Client()
        self.json = json
        self.user = User.objects.create_user(username='regularapi', password='Password123!')
        self.superuser = User.objects.create_superuser(username='superapi', password='Password123!', email='s@x.com')
        self.token = create_access_token(self.user.id)
        self.super_token = create_access_token(self.superuser.id)
        self.truck = Truck.objects.create(registration_no='TRK-TEST-1', capacity=20.0, status='available')

    def test_list_trucks_requires_bearer_auth(self):
        response = self.client.get('/api/trucks/')
        self.assertEqual(response.status_code, 401)

    def test_list_and_get_truck_authorized(self):
        response = self.client.get(
            '/api/trucks/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('items', data)

        detail = self.client.get(
            f'/api/trucks/{self.truck.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()['registration_no'], 'TRK-TEST-1')

    def test_create_truck_success(self):
        payload = {
            'registration_no': 'TRK-NEW-2',
            'capacity': 18.5,
            'status': 'available',
        }
        response = self.client.post(
            '/api/trucks/',
            data=self.json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Truck.objects.filter(registration_no='TRK-NEW-2').exists())

    def test_delete_truck_permission(self):
        # Regular user attempt -> 403
        resp_forbidden = self.client.delete(
            f'/api/trucks/{self.truck.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(resp_forbidden.status_code, 403)
        self.assertTrue(Truck.objects.filter(id=self.truck.id).exists())

        # Superuser attempt -> 200
        resp_ok = self.client.delete(
            f'/api/trucks/{self.truck.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.super_token}'
        )
        self.assertEqual(resp_ok.status_code, 200)
        self.assertFalse(Truck.objects.filter(id=self.truck.id).exists())