from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Truck, Driver, Job


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
