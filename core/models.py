from django.db import models
from django.core.validators import RegexValidator

# regex validators for the models


alphanumeric = RegexValidator(
    regex=r'^[A-Za-z0-9\s\-]+$',
    message='Only letters, numbers, spaces and hyphens allowed'
)

numeric = RegexValidator(
    regex=r'^\+?[0-9\s\-]+$',
    message='Only numbers'
)
class Driver(models.Model):
    name = models.CharField(max_length=255)
    license_no = models.CharField(max_length=255, unique=True, validators=[alphanumeric])
    phone_no = models.CharField(max_length=10, validators=[numeric])
    
    def __str__(self):
        return f"{self.name}: {self.license_no}"

class Truck(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('maintenance', 'Maintenance'),
    ]

    registration_no =models.CharField(max_length=20, unique=True, validators=[alphanumeric])
    capacity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.registration_no} - {self.status}"
    
class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    pick_up_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    cargo = models.TextField(max_length=400)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    assigned_truck = models.ForeignKey(Truck, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    assigned_driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.id} ({self.status})"

class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=500)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user}: {self.action}"