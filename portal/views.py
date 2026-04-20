from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from core.models import Truck, Driver, Job
from .forms import TruckForm, DriverForm, JobForm, AssignJobForm, UpdateStatusForm


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


def register_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('portal:login')
    else:
        form = UserCreationForm()

    return render(request, 'portal/register.html', {'form': form})



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
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete.')
        return redirect('portal:truck_list')

    truck = get_object_or_404(Truck, pk=pk)
    if request.method == 'POST':
        reg = truck.registration_no
        truck.delete()
        messages.success(request, f'Truck {reg} deleted.')
        return redirect('portal:truck_list')
    return render(request, 'portal/trucks/confirm_delete.html', {'truck': truck})


# ─────────────────────────────────────────
# Drivers
# ─────────────────────────────────────────

@login_required
def driver_list(request):
    active_jobs = Job.objects.filter(
        assigned_driver=OuterRef('pk'),
        status__in=['pending', 'in_transit']
    )
    qs = Driver.objects.annotate(has_active_job=Exists(active_jobs)).order_by('id')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portal/drivers/list.html', {'page_obj': page_obj})


@login_required
def driver_create(request):
    form = DriverForm(request.POST or None)
    if form.is_valid():
        driver = form.save()
        messages.success(request, f'Driver {driver.name} created successfully.')
        return redirect('portal:driver_list')
    return render(request, 'portal/drivers/form.html', {
        'form': form,
        'action': 'Create',
        'title': 'Add New Driver',
    })


@login_required
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    form = DriverForm(request.POST or None, instance=driver)
    if form.is_valid():
        form.save()
        messages.success(request, f'Driver {driver.name} updated successfully.')
        return redirect('portal:driver_list')
    return render(request, 'portal/drivers/form.html', {
        'form': form,
        'action': 'Edit',
        'title': f'Edit Driver — {driver.name}',
        'driver': driver,
    })


@login_required
def driver_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete.')
        return redirect('portal:driver_list')

    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        name = driver.name
        driver.delete()
        messages.success(request, f'Driver {name} deleted.')
        return redirect('portal:driver_list')
    return render(request, 'portal/drivers/confirm_delete.html', {'driver': driver})


# ─────────────────────────────────────────
# Jobs
# ─────────────────────────────────────────

@login_required
def job_list(request):
    status_filter = request.GET.get('status', '')
    qs = Job.objects.select_related('assigned_truck', 'assigned_driver').order_by('-created_at')
    if status_filter in ['pending', 'in_transit', 'completed', 'cancelled']:
        qs = qs.filter(status=status_filter)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portal/jobs/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })


@login_required
def job_create(request):
    form = JobForm(request.POST or None)
    if form.is_valid():
        job = form.save()
        messages.success(request, f'Job #{job.id} created successfully.')
        return redirect('portal:job_detail', pk=job.pk)
    return render(request, 'portal/jobs/form.html', {
        'form': form,
        'title': 'Create New Job',
        'action': 'Create',
    })


@login_required
def job_detail(request, pk):
    job = get_object_or_404(
        Job.objects.select_related('assigned_truck', 'assigned_driver'), pk=pk
    )
    assign_form = AssignJobForm() if job.status == 'pending' else None
    status_form = UpdateStatusForm(initial={'status': job.status})
    return render(request, 'portal/jobs/detail.html', {
        'job': job,
        'assign_form': assign_form,
        'status_form': status_form,
    })


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    form = JobForm(request.POST or None, instance=job)
    if form.is_valid():
        form.save()
        messages.success(request, f'Job #{job.id} updated successfully.')
        return redirect('portal:job_detail', pk=job.pk)
    return render(request, 'portal/jobs/form.html', {
        'form': form,
        'title': f'Edit Job #{job.id}',
        'action': 'Edit',
        'job': job,
    })


@login_required
def job_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete.')
        return redirect('portal:job_list')

    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job_id = job.id
        job.delete()
        messages.success(request, f'Job #{job_id} deleted.')
        return redirect('portal:job_list')
    return render(request, 'portal/jobs/confirm_delete.html', {'job': job})


@login_required
def job_assign(request, pk):
    if request.method != 'POST':
        return redirect('portal:job_detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)
    form = AssignJobForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Please select both a truck and a driver.')
        return redirect('portal:job_detail', pk=pk)

    truck = form.cleaned_data['truck']
    driver = form.cleaned_data['driver']

    # Business rule: truck must be available
    if truck.status != 'available':
        messages.error(request, f'Truck {truck.registration_no} is no longer available.')
        return redirect('portal:job_detail', pk=pk)

    # Business rule: driver must not have an active job
    if Job.objects.filter(assigned_driver=driver, status__in=['pending', 'in_transit']).exists():
        messages.error(request, f'Driver {driver.name} already has an active job.')
        return redirect('portal:job_detail', pk=pk)

    job.assigned_truck = truck
    job.assigned_driver = driver
    job.status = 'in_transit'
    job.save()

    truck.status = 'in_transit'
    truck.save()

    messages.success(request, f'Job #{pk} assigned to {driver.name} on truck {truck.registration_no}.')
    return redirect('portal:job_detail', pk=pk)


@login_required
def job_update_status(request, pk):
    if request.method != 'POST':
        return redirect('portal:job_detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)
    form = UpdateStatusForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Invalid status selected.')
        return redirect('portal:job_detail', pk=pk)

    old_status = job.status
    new_status = form.cleaned_data['status']
    job.status = new_status
    job.save()

    if new_status in ['completed', 'cancelled'] and job.assigned_truck:
        job.assigned_truck.status = 'available'
        job.assigned_truck.save()

    messages.success(request, f'Job #{pk} status changed from {old_status} to {new_status}.')
    return redirect('portal:job_detail', pk=pk)
