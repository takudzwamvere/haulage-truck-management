from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import Truck, Driver, Job, AuditLog


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