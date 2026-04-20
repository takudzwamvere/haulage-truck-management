from django import forms
from django.db.models import Exists, OuterRef
from core.models import Truck, Driver, Job

_INPUT = 'form-control'
_SELECT = 'form-select'



class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['registration_no', 'capacity', 'status']
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
        }
        labels = {
            'registration_no': 'Registration Number',
            'capacity': 'Capacity (tonnes)',
            'status': 'Status',
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'license_no', 'phone_no']
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
        }
        labels = {
            'name': 'Full Name',
            'license_no': 'License Number',
            'phone_no': 'Phone Number',
        }


class JobForm(forms.ModelForm):
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
        active_jobs = Job.objects.filter(
            assigned_driver=OuterRef('pk'),
            status__in=['pending', 'in_transit']
        )
        self.fields['truck'].queryset = Truck.objects.filter(status='available')
        self.fields['driver'].queryset = Driver.objects.annotate(
            has_active_job=Exists(active_jobs)
        ).filter(has_active_job=False)


class UpdateStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('in_transit', 'In Transit'),
        ('completed',  'Completed'),
        ('cancelled',  'Cancelled'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': _SELECT}),
        label='New Status',
    )
