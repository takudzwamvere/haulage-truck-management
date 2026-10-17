from ninja import Router, File, UploadedFile
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from ninja.errors import HttpError
from .models import Truck, Driver, Job, AuditLog, validate_image_file
from .schemas import (
    TruckIn, TruckOut, TruckPatch,
    DriverIn, DriverOut, DriverPatch, DriverMePatch,
    JobIn, JobOut,
    AssignJob, UpdateStatus,
    ErrorOut, LoginIn, TokenOut
)
from ninja.pagination import paginate, PageNumberPagination
import logging
from django.contrib.auth import authenticate
from .auth import create_access_token, AuthBearer

logger = logging.getLogger('core')

auth_router = Router(tags=["Auth"])
truck_router = Router(tags=["Trucks"])
driver_router = Router(tags=["Drivers"])
job_router = Router(tags=["Jobs"])


def is_driver(user):
    """Check if user is a driver (has linked driver_profile)."""
    return bool(hasattr(user, 'driver_profile') and user.driver_profile is not None)


@auth_router.post('/login/', response={200: TokenOut, 401: ErrorOut})
def login(request, payload: LoginIn):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        logger.warning(f'Failed login attempt for username: {payload.username}')
        return 401, {'detail': 'Invalid username or password'}
    logger.info(f'User {payload.username} logged in')
    token = create_access_token(user.id)
    return 200, {'access_token': token, 'token_type': 'bearer'}


@truck_router.get('/', response=list[TruckOut])
@paginate(PageNumberPagination, page_size=10)
def list_trucks(request):
    return Truck.objects.all()


@truck_router.post('/', response={200: TruckOut, 400: ErrorOut, 403: ErrorOut})
def create_truck(request, payload: TruckIn):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers cannot create trucks.'}
    truck = Truck(**payload.model_dump())
    try:
        truck.full_clean()
    except ValidationError as e:
        errors = '; '.join(
            f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
        )
        return 400, {'detail': errors}
    truck.save()
    AuditLog.objects.create(user=request.user.username, action=f'Truck {truck.registration_no} created')
    logger.info(f'Truck {truck.registration_no} created')
    return 200, truck


@truck_router.get('/{truck_id}/', response=TruckOut)
def get_truck(request, truck_id: int):
    return get_object_or_404(Truck, id=truck_id)


@truck_router.patch('/{truck_id}/', response={200: TruckOut, 400: ErrorOut, 403: ErrorOut})
def update_truck(request, truck_id: int, payload: TruckPatch):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Only staff and administrators can edit trucks.'}
    truck = get_object_or_404(Truck, id=truck_id)
    for attr, value in payload.model_dump().items():
        if value is not None:
            setattr(truck, attr, value)
    try:
        truck.full_clean()
    except ValidationError as e:
        errors = '; '.join(
            f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
        )
        return 400, {'detail': errors}
    truck.save()
    AuditLog.objects.create(user=request.user.username, action=f'Truck {truck.registration_no} updated')
    logger.info(f'Truck {truck.registration_no} updated')
    return 200, truck


@truck_router.delete('/{truck_id}/', response={200: dict, 403: ErrorOut})
def delete_truck(request, truck_id: int):
    if not request.user.is_superuser:
        return 403, {'detail': 'Only administrators can delete trucks.'}
    truck = get_object_or_404(Truck, id=truck_id)
    logger.info(f'Truck {truck.registration_no} deleted by {request.user.username}')
    AuditLog.objects.create(user=request.user.username, action=f'Truck {truck.registration_no} deleted')
    truck.delete()
    return 200, {'success': True}


# ─── Driver Routes ───────────────────────────────────────────────

@driver_router.get('/me', response={200: DriverOut, 404: ErrorOut})
def get_my_driver_profile(request):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver:
        return 404, {'detail': 'No driver profile linked to current user'}
    return 200, driver


@driver_router.patch('/me', response={200: DriverOut, 400: ErrorOut, 404: ErrorOut})
def update_my_driver_profile(request, payload: DriverMePatch):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver:
        return 404, {'detail': 'No driver profile linked to current user'}

    if payload.name is not None and payload.name != driver.name:
        return 400, {'detail': 'name is read-only and cannot be updated.'}
    if payload.license_no is not None and payload.license_no != driver.license_no:
        return 400, {'detail': 'license_no is read-only and cannot be updated.'}

    if payload.phone_no is not None:
        driver.phone_no = payload.phone_no
        try:
            driver.full_clean()
        except ValidationError as e:
            errors = '; '.join(f'{f}: {", ".join(m)}' for f, m in e.message_dict.items())
            return 400, {'detail': errors}
        driver.save()
        AuditLog.objects.create(
            user=request.user.username,
            action=f'Updated driver self-service phone number to {driver.phone_no}'
        )
    return 200, driver


@driver_router.post('/me/photo/', response={200: DriverOut, 400: ErrorOut, 404: ErrorOut})
def update_my_driver_photo(request, file: UploadedFile = File(...)):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver:
        return 404, {'detail': 'No driver profile linked to current user'}
    try:
        validate_image_file(file)
    except ValidationError as e:
        return 400, {'detail': '; '.join(e.messages)}
    driver.photo = file
    driver.save()
    AuditLog.objects.create(
        user=request.user.username,
        action=f'Updated driver photo for {driver.name}'
    )
    return 200, driver


@driver_router.get('/', response=list[DriverOut])
@paginate(PageNumberPagination, page_size=10)
def list_drivers(request):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return Driver.objects.filter(id=request.user.driver_profile.id)
    return Driver.objects.all()


@driver_router.post('/', response={200: DriverOut, 400: ErrorOut, 403: ErrorOut})
def create_driver(request, payload: DriverIn):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers cannot create driver records.'}
    driver = Driver(**payload.model_dump())
    try:
        driver.full_clean()
    except ValidationError as e:
        errors = '; '.join(
            f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
        )
        return 400, {'detail': errors}
    driver.save()
    AuditLog.objects.create(user=request.user.username, action=f'Driver {driver.name} created')
    logger.info(f'Driver {driver.name} created')
    return 200, driver


@driver_router.get('/{driver_id}/', response={200: DriverOut, 403: ErrorOut, 404: ErrorOut})
def get_driver(request, driver_id: int):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        if driver_id != request.user.driver_profile.id:
            return 403, {'detail': 'Drivers can only access their own profile.'}
    return 200, get_object_or_404(Driver, id=driver_id)


@driver_router.patch('/{driver_id}/', response={200: DriverOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def update_driver(request, driver_id: int, payload: DriverPatch):
    driver = get_object_or_404(Driver, id=driver_id)
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        if driver_id != request.user.driver_profile.id:
            return 403, {'detail': 'Drivers can only update their own profile.'}
        if payload.name is not None and payload.name != driver.name:
            return 400, {'detail': 'name is read-only and cannot be updated.'}
        if payload.license_no is not None and payload.license_no != driver.license_no:
            return 400, {'detail': 'license_no is read-only and cannot be updated.'}

    for attr, value in payload.model_dump().items():
        if value is not None:
            setattr(driver, attr, value)
    try:
        driver.full_clean()
    except ValidationError as e:
        errors = '; '.join(
            f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
        )
        return 400, {'detail': errors}
    driver.save()
    AuditLog.objects.create(user=request.user.username, action=f'Driver {driver.name} updated')
    logger.info(f'Driver {driver.name} updated')
    return 200, driver


@driver_router.delete('/{driver_id}/', response={200: dict, 403: ErrorOut})
def delete_driver(request, driver_id: int):
    if not request.user.is_superuser:
        return 403, {'detail': 'Only administrators can delete drivers.'}
    driver = get_object_or_404(Driver, id=driver_id)
    logger.info(f'Driver {driver.name} deleted by {request.user.username}')
    AuditLog.objects.create(user=request.user.username, action=f'Driver {driver.name} deleted')
    driver.delete()
    return 200, {'success': True}


# ─── Job Routes ──────────────────────────────────────────────────

@job_router.get('/', response=list[JobOut])
@paginate(PageNumberPagination, page_size=10)
def list_jobs(request):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return Job.objects.select_related('assigned_truck', 'assigned_driver').filter(assigned_driver=request.user.driver_profile)
    return Job.objects.select_related('assigned_truck', 'assigned_driver').all()


@job_router.post('/', response={200: JobOut, 400: ErrorOut, 403: ErrorOut})
def create_job(request, payload: JobIn):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers have read-only access to assigned jobs.'}
    job = Job(**payload.model_dump())
    try:
        job.full_clean()
    except ValidationError as e:
        errors = '; '.join(
            f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
        )
        return 400, {'detail': errors}
    job.save()
    AuditLog.objects.create(user=request.user.username, action=f'Job #{job.id} created')
    logger.info(f'Job {job.id} created')
    return 200, job


@job_router.get('/{job_id}/', response={200: JobOut, 403: ErrorOut, 404: ErrorOut})
def get_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        if job.assigned_driver != request.user.driver_profile:
            return 403, {'detail': 'Drivers can only view jobs assigned to them.'}
    return 200, job


@job_router.delete('/{job_id}/', response={200: dict, 403: ErrorOut})
def delete_job(request, job_id: int):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers have read-only access to assigned jobs.'}
    if not request.user.is_superuser:
        return 403, {'detail': 'Only administrators can delete jobs.'}
    job = get_object_or_404(Job, id=job_id)
    logger.info(f'Job {job_id} deleted by {request.user.username}')
    AuditLog.objects.create(user=request.user.username, action=f'Job #{job_id} deleted')
    job.delete()
    return 200, {'success': True}


@job_router.post('/{job_id}/assign/', response={200: JobOut, 400: ErrorOut, 403: ErrorOut})
def assign_job(request, job_id: int, payload: AssignJob):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers have read-only access to assigned jobs.'}
    with transaction.atomic():
        # Fetch with lock to prevent race conditions
        job = get_object_or_404(Job.objects.select_for_update(), id=job_id)
        truck = get_object_or_404(Truck.objects.select_for_update(), id=payload.truck_id)
        driver = get_object_or_404(Driver.objects.select_for_update(), id=payload.driver_id)

        # Only 'pending' jobs can be assigned (state machine guard)
        if job.status != 'pending':
            logger.warning(f'Attempted to assign job {job_id} with status {job.status!r}')
            return 400, {'detail': f'Only pending jobs can be assigned. Current status: {job.status}'}

        if truck.status != 'available':
            logger.warning(f'Attempted to assign unavailable truck {truck.registration_no} to job {job_id}')
            return 400, {'detail': f'Truck {truck.registration_no} is not available. Current status: {truck.status}'}

        active_job = Job.objects.filter(
            assigned_driver=driver,
            status__in=['pending', 'in_transit']
        ).exists()
        if active_job:
            logger.warning(f'Attempted to assign busy driver {driver.name} to job {job_id}')
            return 400, {'detail': f'Driver {driver.name} already has an active job'}

        job.assigned_truck = truck
        job.assigned_driver = driver
        job.status = 'in_transit'
        job.save()

        truck.status = 'in_transit'
        truck.save()

    AuditLog.objects.create(
        user=request.user.username,
        action=f'Job #{job_id} assigned to {driver.name} on truck {truck.registration_no}'
    )
    logger.info(f'Job #{job_id} assigned to {driver.name} on truck {truck.registration_no}')
    return 200, job


@job_router.patch('/{job_id}/status/', response={200: JobOut, 400: ErrorOut, 403: ErrorOut})
def update_job_status(request, job_id: int, payload: UpdateStatus):
    if is_driver(request.user) and not request.user.is_superuser and not request.user.is_staff:
        return 403, {'detail': 'Drivers have read-only access to assigned jobs.'}
    with transaction.atomic():
        job = get_object_or_404(Job.objects.select_for_update(), id=job_id)

        old_status = job.status
        job.status = payload.status
        try:
            job.full_clean()
        except ValidationError as e:
            errors = '; '.join(
                f'{field}: {", ".join(msgs)}' for field, msgs in e.message_dict.items()
            )
            return 400, {'detail': errors}
        job.save()

        if payload.status in ['completed', 'cancelled']:
            if job.assigned_truck:
                truck = Truck.objects.select_for_update().get(id=job.assigned_truck.id)
                truck.status = 'available'
                truck.save()

    AuditLog.objects.create(
        user=request.user.username,
        action=f'Job #{job_id} status changed from {old_status} to {payload.status}'
    )
    logger.info(f'Job {job_id} status changed from {old_status} to {payload.status}')
    return 200, job