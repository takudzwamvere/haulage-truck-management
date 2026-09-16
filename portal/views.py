import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Count, Q
from django.db import transaction
from django.views.decorators.http import require_POST
from core.models import Truck, Driver, Job, AuditLog
from .forms import TruckForm, DriverForm, JobForm, AssignJobForm, UpdateStatusForm

logger = logging.getLogger('core')


def audit(username, action):
    """Log an audit trail entry. Always pass a username string."""
    AuditLog.objects.create(user=username, action=action)


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
            audit(username, 'Logged in via portal')
            return redirect('portal:dashboard')

        # Check if user exists but is inactive (pending admin approval)
        try:
            inactive_user = User.objects.get(username=username)
            if not inactive_user.is_active:
                messages.warning(request, 'Your account is pending admin approval. Please wait for an administrator to activate your account.')
                return render(request, 'portal/login.html', {'attempted_username': username})
        except User.DoesNotExist:
            pass

        audit(username, 'Failed login attempt')
        messages.error(request, 'Invalid username or password. Please try again.')
        return render(request, 'portal/login.html', {'attempted_username': username})

    return render(request, 'portal/login.html')


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        audit(request.user.username, 'Logged out')
    logout(request)
    return redirect('portal:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            audit(user.username, 'Account registered (pending approval)')
            messages.success(request, 'Account created! An administrator must approve your account before you can log in.')
            return redirect('portal:login')
    else:
        form = UserCreationForm()

    return render(request, 'portal/register.html', {'form': form})


# ─── User Management (superuser only) ───────────────────────────

@login_required
def pending_users_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('portal:dashboard')

    pending = User.objects.filter(is_active=False, is_superuser=False).order_by('-date_joined')
    return render(request, 'portal/pending_users.html', {'pending_users': pending})


@login_required
@require_POST
def approve_user_view(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to approve users.')
        return redirect('portal:dashboard')

    user = get_object_or_404(User, pk=pk, is_active=False)
    user.is_active = True
    user.save()
    audit(request.user.username, f'Approved user {user.username}')
    messages.success(request, f'User "{user.username}" has been approved and can now log in.')
    return redirect('portal:pending_users')


@login_required
@require_POST
def reject_user_view(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to reject users.')
        return redirect('portal:dashboard')

    user = get_object_or_404(User, pk=pk, is_active=False)
    username = user.username
    user.delete()
    audit(request.user.username, f'Rejected and deleted user {username}')
    messages.success(request, f'User "{username}" has been rejected and removed.')
    return redirect('portal:pending_users')


# ─── Dashboard ───────────────────────────────────────────────────

@login_required
def dashboard(request):
    truck_stats = Truck.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        in_transit=Count('id', filter=Q(status='in_transit')),
        maintenance=Count('id', filter=Q(status='maintenance')),
    )
    job_stats = Job.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        active=Count('id', filter=Q(status='in_transit')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled')),
    )
    context = {
        'total_trucks':       truck_stats['total'],
        'available_trucks':   truck_stats['available'],
        'in_transit_trucks':  truck_stats['in_transit'],
        'maintenance_trucks': truck_stats['maintenance'],
        'total_drivers':      Driver.objects.count(),
        'total_jobs':         job_stats['total'],
        'pending_jobs':       job_stats['pending'],
        'active_jobs':        job_stats['active'],
        'completed_jobs':     job_stats['completed'],
        'cancelled_jobs':     job_stats['cancelled'],
        'recent_jobs':        Job.objects.select_related(
                                  'assigned_truck', 'assigned_driver'
                              ).order_by('-created_at')[:5],
    }
    return render(request, 'portal/dashboard.html', context)


# ─── Trucks ──────────────────────────────────────────────────────

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
        audit(request.user.username, f'Created truck {truck.registration_no}')
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
        audit(request.user.username, f'Updated truck {truck.registration_no}')
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
        audit(request.user.username, f'Deleted truck {reg}')
        messages.success(request, f'Truck {reg} deleted.')
        return redirect('portal:truck_list')
    return render(request, 'portal/trucks/confirm_delete.html', {'truck': truck})


# ─── Drivers ─────────────────────────────────────────────────────

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
        audit(request.user.username, f'Created driver {driver.name}')
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
        audit(request.user.username, f'Updated driver {driver.name}')
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
        audit(request.user.username, f'Deleted driver {name}')
        messages.success(request, f'Driver {name} deleted.')
        return redirect('portal:driver_list')
    return render(request, 'portal/drivers/confirm_delete.html', {'driver': driver})


# ─── Jobs ────────────────────────────────────────────────────────

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
        audit(request.user.username, f'Created job #{job.id}')
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
        audit(request.user.username, f'Updated job #{job.id}')
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
        audit(request.user.username, f'Deleted job #{job_id}')
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

    with transaction.atomic():
        # Re-fetch with lock to prevent race conditions
        truck = Truck.objects.select_for_update().get(pk=form.cleaned_data['truck'].pk)
        driver = Driver.objects.select_for_update().get(pk=form.cleaned_data['driver'].pk)
        locked_job = Job.objects.select_for_update().get(pk=pk)

        # Only 'pending' jobs can be assigned (state machine guard)
        if locked_job.status != 'pending':
            audit(request.user.username, f'Attempted to assign job #{pk} with status {locked_job.status!r}')
            messages.error(request, f'Only pending jobs can be assigned. Current status: {locked_job.status}.')
            return redirect('portal:job_detail', pk=pk)

        if truck.status != 'available':
            audit(request.user.username, f'Attempted to assign unavailable truck {truck.registration_no} to job #{pk}')
            messages.error(request, f'Truck {truck.registration_no} is no longer available.')
            return redirect('portal:job_detail', pk=pk)

        if Job.objects.filter(assigned_driver=driver, status__in=['pending', 'in_transit']).exists():
            audit(request.user.username, f'Attempted to assign busy driver {driver.name} to job #{pk}')
            messages.error(request, f'Driver {driver.name} already has an active job.')
            return redirect('portal:job_detail', pk=pk)

        locked_job.assigned_truck = truck
        locked_job.assigned_driver = driver
        locked_job.status = 'in_transit'
        locked_job.save()

        truck.status = 'in_transit'
        truck.save()

    audit(request.user.username, f'Assigned job #{pk} to {driver.name} on truck {truck.registration_no}')
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

    new_status = form.cleaned_data['status']
    old_status = job.status

    # Validate status transition
    allowed = Job.VALID_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        messages.error(request, f'Cannot change status from {old_status} to {new_status}.')
        return redirect('portal:job_detail', pk=pk)

    with transaction.atomic():
        locked_job = Job.objects.select_for_update().get(pk=pk)

        locked_job.status = new_status
        locked_job.save()

        if new_status in ['completed', 'cancelled'] and locked_job.assigned_truck:
            truck = Truck.objects.select_for_update().get(pk=locked_job.assigned_truck.pk)
            truck.status = 'available'
            truck.save()

    audit(request.user.username, f'Changed job #{pk} status from {old_status} to {new_status}')
    messages.success(request, f'Job #{pk} status changed from {old_status} to {new_status}.')
    return redirect('portal:job_detail', pk=pk)


# ─── Logs ────────────────────────────────────────────────────────

@login_required
def logs_view(request):
    if request.user.is_superuser:
        logs = AuditLog.objects.all()[:200]
    else:
        logs = AuditLog.objects.filter(user=request.user.username)[:200]

    lines = [
        f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.user}: {log.action}"
        for log in logs
    ]

    if not lines:
        lines = ['No activity recorded yet.']

    return render(request, 'portal/logs.html', {'lines': lines})