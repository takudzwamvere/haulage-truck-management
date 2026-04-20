from django import forms
from core.models import Truck

_INPUT = (
    'w-full px-4 py-2.5 rounded-xl bg-white border border-slate-300 '
    'text-slate-800 text-sm shadow-sm '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent '
    'transition-shadow'
)

_SELECT = (
    'w-full px-4 py-2.5 rounded-xl bg-white border border-slate-300 '
    'text-slate-800 text-sm shadow-sm cursor-pointer '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent '
    'transition-shadow'
)


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
