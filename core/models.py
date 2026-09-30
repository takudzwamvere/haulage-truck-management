from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# regex validators for the models
ALPHANUMERIC_MSG = 'Only letters, numbers, spaces and hyphens allowed'
NUMERIC_MSG = 'Only numbers, spaces and hyphens allowed'

alphanumeric = RegexValidator(
    regex=r'^[A-Za-z0-9\s\-]+$',
    message=ALPHANUMERIC_MSG
)

numeric = RegexValidator(
    regex=r'^\+?[0-9\s\-]+$',
    message=NUMERIC_MSG
)


class Driver(models.Model):
    """Represents a registered haulage driver.

    Drivers are associated with Job assignments and must hold a unique
    licence number. Phone numbers are validated to contain only digits,
    spaces, and hyphens.
    """
    name = models.CharField(max_length=255)
    license_no = models.CharField(max_length=255, unique=True, validators=[alphanumeric])
    phone_no = models.CharField(max_length=20, validators=[numeric])

    def __str__(self):
        """Return name and licence number."""
        return f"{self.name}: {self.license_no}"


class Truck(models.Model):
    """Represents a haulage vehicle in the fleet and its availability state.

    Status progresses through 'available', 'in_transit', and 'maintenance'.
    Capacity is stored in tonnes to two decimal places.
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('maintenance', 'Maintenance'),
    ]

    registration_no = models.CharField(max_length=20, unique=True, validators=[alphanumeric])
    capacity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)

    def __str__(self):
        """Return registration number and current status."""
        return f"{self.registration_no} - {self.status}"


class Job(models.Model):
    """Represents a cargo delivery assignment with status progression rules.

    Status transitions are strictly enforced: pending → in_transit or cancelled,
    in_transit → completed or cancelled. Terminal states (completed, cancelled)
    cannot be changed. Pick-up and delivery locations must differ.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # State machine: maps each status to the statuses it can legally transition to.
    # Terminal states (completed, cancelled) have empty lists — no further moves allowed.
    VALID_TRANSITIONS = {
        'pending': ['in_transit', 'cancelled'],
        'in_transit': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': [],
    }

    pick_up_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    cargo = models.TextField(max_length=400)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending', db_index=True)
    assigned_truck = models.ForeignKey(Truck, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    assigned_driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return job ID and current status."""
        return f"Job {self.id} ({self.status})"

    def clean(self):
        """Validate location uniqueness and enforce status transition rules."""
        if self.pick_up_location and self.delivery_location:
            if self.pick_up_location.strip().lower() == self.delivery_location.strip().lower():
                raise ValidationError({
                    'delivery_location': 'Delivery location cannot be the same as pick up location.'
                })

        # Validate status transitions (skip for new objects)
        if self.pk:
            try:
                old = Job.objects.get(pk=self.pk)
            except Job.DoesNotExist:
                return
            if old.status != self.status:
                allowed = self.VALID_TRANSITIONS.get(old.status, [])
                if self.status not in allowed:
                    raise ValidationError({
                        'status': f'Cannot change status from {old.status} to {self.status}.'
                    })


class AuditLog(models.Model):
    """Immutable audit trail record for user actions and system events.

    Records are ordered by timestamp descending. The user field stores the
    username string at the time of the action; records are never updated.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=500)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"[{self.timestamp}] {self.user}: {self.action}"