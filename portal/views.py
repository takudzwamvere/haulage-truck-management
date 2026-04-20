from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from core.models import Truck, Driver, Job
from .forms import TruckForm


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    return redirect('portal:login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')
        messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'portal/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('portal:login')


@login_required
def dashboard(request):
    context = {
        # Truck stats
        'total_trucks':       Truck.objects.count(),
        'available_trucks':   Truck.objects.filter(status='available').count(),
        'in_transit_trucks':  Truck.objects.filter(status='in_transit').count(),
        'maintenance_trucks': Truck.objects.filter(status='maintenance').count(),

        # Driver stats
        'total_drivers': Driver.objects.count(),

        # Job stats
        'total_jobs':     Job.objects.count(),
        'pending_jobs':   Job.objects.filter(status='pending').count(),
        'active_jobs':    Job.objects.filter(status='in_transit').count(),
        'completed_jobs': Job.objects.filter(status='completed').count(),
        'cancelled_jobs': Job.objects.filter(status='cancelled').count(),

        # Recent activity
        'recent_jobs': Job.objects.select_related(
            'assigned_truck', 'assigned_driver'
        ).order_by('-created_at')[:5],
    }
    return render(request, 'portal/dashboard.html', context)


# ─────────────────────────────────────────
# Trucks
# ─────────────────────────────────────────

@login_required
def truck_list(request):
    qs = Truck.objects.order_by('id')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portal/trucks/list.html', {'page_obj': page_obj})


@login_required
def truck_create(request):
    form = TruckForm(request.POST or None)
    if form.is_valid():
        truck = form.save()
        messages.success(request, f'Truck {truck.registration_no} created successfully.')
        return redirect('portal:truck_list')
    return render(request, 'portal/trucks/form.html', {
        'form': form,
        'action': 'Create',
        'title': 'Add New Truck',
    })


@login_required
def truck_edit(request, pk):
    truck = get_object_or_404(Truck, pk=pk)
    form = TruckForm(request.POST or None, instance=truck)
    if form.is_valid():
        form.save()
        messages.success(request, f'Truck {truck.registration_no} updated successfully.')
        return redirect('portal:truck_list')
    return render(request, 'portal/trucks/form.html', {
        'form': form,
        'action': 'Edit',
        'title': f'Edit Truck — {truck.registration_no}',
        'truck': truck,
    })


@login_required
def truck_delete(request, pk):
    truck = get_object_or_404(Truck, pk=pk)
    if request.method == 'POST':
        reg = truck.registration_no
        truck.delete()
        messages.success(request, f'Truck {reg} deleted.')
        return redirect('portal:truck_list')
    return render(request, 'portal/trucks/confirm_delete.html', {'truck': truck})
