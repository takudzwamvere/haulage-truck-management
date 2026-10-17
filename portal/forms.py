from django import forms
from django.db.models import Exists, OuterRef
from core.models import Truck, Driver, Job

_INPUT = 'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm'
_SELECT = 'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 bg-white shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm'



from django.contrib.auth.models import User

PHOTO_HELP_TEXT = "Max file size: 2 MB. Formats: JPEG, PNG, WebP. (Note: Vercel serverless request body is capped at 4.5 MB)."


class TruckForm(forms.ModelForm):
    """Form for adding and updating fleet trucks."""
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Truck photos editable by staff and admin only
        if user and not (user.is_superuser or user.is_staff):
            if 'photo' in self.fields:
                del self.fields['photo']

    class Meta:
        model = Truck
        fields = ['registration_no', 'capacity', 'status', 'photo']
        widgets = {
            'registration_no': forms.TextInput(attrs={
                'placeholder': 'e.g. ABC-1234',
                'class': _INPUT,
            }),
            'capacity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 5000',
                'step': '0.01',
                'class': _INPUT,
            }),
            'status': forms.Select(attrs={
                'class': _SELECT,
            }),
            'photo': forms.FileInput(attrs={
                'class': _INPUT,
                'accept': 'image/jpeg,image/png,image/webp',
            }),
        }
        labels = {
            'registration_no': 'Registration Number',
            'capacity': 'Capacity (tonnes)',
            'status': 'Status',
            'photo': 'Truck Photo',
        }
        help_texts = {
            'photo': PHOTO_HELP_TEXT,
        }


class DriverForm(forms.ModelForm):
    """Form for registering and updating driver profiles by administrators."""
    class Meta:
        model = Driver
        fields = ['name', 'license_no', 'phone_no', 'user', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. John Doe',
                'class': _INPUT,
            }),
            'license_no': forms.TextInput(attrs={
                'placeholder': 'e.g. DL-2024-001',
                'class': _INPUT,
            }),
            'phone_no': forms.TextInput(attrs={
                'placeholder': 'e.g. +263771234567',
                'class': _INPUT,
            }),
            'user': forms.Select(attrs={
                'class': _SELECT,
            }),
            'photo': forms.FileInput(attrs={
                'class': _INPUT,
                'accept': 'image/jpeg,image/png,image/webp',
            }),
        }
        labels = {
            'name': 'Full Name',
            'license_no': 'License Number',
            'phone_no': 'Phone Number',
            'user': 'Linked User Account',
            'photo': 'Driver Photo',
        }
        help_texts = {
            'photo': PHOTO_HELP_TEXT,
            'user': 'Optionally link a user account for driver self-service portal access.',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['user'].empty_label = '— No linked user account —'
        if user and not (user.is_superuser or user.is_staff):
            if 'user' in self.fields:
                del self.fields['user']


class DriverProfileForm(forms.ModelForm):
    """Self-service form for drivers: phone_no and photo only. name and license_no cannot be changed."""
    class Meta:
        model = Driver
        fields = ['phone_no', 'photo']
        widgets = {
            'phone_no': forms.TextInput(attrs={
                'placeholder': 'e.g. +263771234567',
                'class': _INPUT,
            }),
            'photo': forms.FileInput(attrs={
                'class': _INPUT,
                'accept': 'image/jpeg,image/png,image/webp',
            }),
        }
        labels = {
            'phone_no': 'Phone Number',
            'photo': 'Profile Photo',
        }
        help_texts = {
            'photo': PHOTO_HELP_TEXT,
        }


class JobForm(forms.ModelForm):
    """Form for logging and modifying freight jobs."""
    class Meta:
        model = Job
        fields = ['pick_up_location', 'delivery_location', 'cargo']
        widgets = {
            'pick_up_location': forms.TextInput(attrs={
                'placeholder': 'e.g. Harare CBD',
                'class': _INPUT,
            }),
            'delivery_location': forms.TextInput(attrs={
                'placeholder': 'e.g. Bulawayo Depot',
                'class': _INPUT,
            }),
            'cargo': forms.Textarea(attrs={
                'placeholder': 'Describe the cargo being transported...',
                'rows': 3,
                'class': _INPUT,
            }),
        }
        labels = {
            'pick_up_location': 'Pickup Location',
            'delivery_location': 'Delivery Location',
            'cargo': 'Cargo Description',
        }


class AssignJobForm(forms.Form):
    """Form for assigning an available truck and free driver to a pending job."""
    truck = forms.ModelChoiceField(
        queryset=Truck.objects.none(),
        widget=forms.Select(attrs={'class': _SELECT}),
        label='Assign Truck',
        empty_label='— Select available truck —',
    )
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.none(),
        widget=forms.Select(attrs={'class': _SELECT}),
        label='Assign Driver',
        empty_label='— Select free driver —',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # grabbing jobs that the driver is currently assigned to (using OuterRef so we can check it in the subquery)
        active_jobs = Job.objects.filter(
            assigned_driver=OuterRef('pk'),
            status__in=['pending', 'in_transit']
        )
        self.fields['truck'].queryset = Truck.objects.filter(status='available')
        self.fields['driver'].queryset = Driver.objects.annotate(
            has_active_job=Exists(active_jobs)
        ).filter(has_active_job=False)


class UpdateStatusForm(forms.Form):
    """Form for transitioning a job through valid lifecycle states."""
    STATUS_LABELS = {
        'pending':    'Pending',
        'in_transit': 'In Transit',
        'completed':  'Completed',
        'cancelled':  'Cancelled',
    }
    status = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': _SELECT}),
        label='New Status',
    )

    def __init__(self, *args, current_status=None, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Job
        if current_status is not None:
            valid_next = Job.VALID_TRANSITIONS.get(current_status, [])
            self.fields['status'].choices = [
                (s, self.STATUS_LABELS[s]) for s in valid_next
            ]
        else:
            # Fallback: show all choices (e.g. when current_status is unknown)
            self.fields['status'].choices = list(self.STATUS_LABELS.items())
