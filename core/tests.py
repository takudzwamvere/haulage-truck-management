from django.test import TestCase
from core.models import Truck, Driver, Job


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