from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Truck, Driver, Job
from .schemas import (
    TruckIn, TruckOut,
    DriverIn, DriverOut,
    JobIn, JobOut,
    AssignJob, UpdateStatus,
    ErrorOut
)
from ninja.pagination import paginate, PageNumberPagination
import logging

logger = logging.getLogger('core')

truck_router = Router(tags=["Trucks"])
driver_router = Router(tags=["Drivers"])
job_router = Router(tags=["Jobs"])


# Trucks

@truck_router.get('/', response=list[TruckOut])
@paginate(PageNumberPagination, page_size=10)
def list_trucks(request):
    return Truck.objects.all()


@truck_router.post('/', response=TruckOut)
def create_truck(request, payload: TruckIn):
    truck = Truck.objects.create(**payload.dict())
    logger.info(f'Truck {truck.registration_no} created')
    return truck


@truck_router.get('/{truck_id}/', response=TruckOut)
def get_truck(request, truck_id: int):
    return get_object_or_404(Truck, id=truck_id)


@truck_router.patch('/{truck_id}/', response=TruckOut)
def update_truck(request, truck_id: int, payload: TruckIn):
    truck = get_object_or_404(Truck, id=truck_id)
    for attr, value in payload.dict().items():
        setattr(truck, attr, value)
    truck.save()
    logger.info(f'Truck {truck.registration_no} updated')
    return truck


@truck_router.delete('/{truck_id}/')
def delete_truck(request, truck_id: int):
    truck = get_object_or_404(Truck, id=truck_id)
    logger.info(f'Truck {truck.registration_no} deleted')
    truck.delete()
    return {'success': True}


# Drivers

@driver_router.get('/', response=list[DriverOut])
@paginate(PageNumberPagination, page_size=10)
def list_drivers(request):
    return Driver.objects.all()


@driver_router.post('/', response=DriverOut)
def create_driver(request, payload: DriverIn):
    driver = Driver.objects.create(**payload.dict())
    logger.info(f'Driver {driver.name} created')
    return driver


@driver_router.get('/{driver_id}/', response=DriverOut)
def get_driver(request, driver_id: int):
    return get_object_or_404(Driver, id=driver_id)


@driver_router.patch('/{driver_id}/', response=DriverOut)
def update_driver(request, driver_id: int, payload: DriverIn):
    driver = get_object_or_404(Driver, id=driver_id)
    for attr, value in payload.dict().items():
        setattr(driver, attr, value)
    driver.save()
    logger.info(f'Driver {driver.name} updated')
    return driver


@driver_router.delete('/{driver_id}/')
def delete_driver(request, driver_id: int):
    driver = get_object_or_404(Driver, id=driver_id)
    logger.info(f'Driver {driver.name} deleted')
    driver.delete()
    return {'success': True}


# Jobs

@job_router.get('/', response=list[JobOut])
@paginate(PageNumberPagination, page_size=10)
def list_jobs(request):
    return Job.objects.select_related('assigned_truck', 'assigned_driver').all()


@job_router.post('/', response=JobOut)
def create_job(request, payload: JobIn):
    job = Job.objects.create(**payload.dict())
    logger.info(f'Job {job.id} created from {job.pick_up_location} to {job.delivery_location}')
    return job


@job_router.get('/{job_id}/', response=JobOut)
def get_job(request, job_id: int):
    return get_object_or_404(Job, id=job_id)


@job_router.delete('/{job_id}/')
def delete_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    logger.info(f'Job {job_id} deleted')
    job.delete()
    return {'success': True}


@job_router.post('/{job_id}/assign/', response={200: JobOut, 400: ErrorOut})
def assign_job(request, job_id: int, payload: AssignJob):
    job = get_object_or_404(Job, id=job_id)
    truck = get_object_or_404(Truck, id=payload.truck_id)
    driver = get_object_or_404(Driver, id=payload.driver_id)

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

    logger.info(f'Job {job_id} assigned to truck {truck.registration_no} and driver {driver.name}')
    return job


@job_router.patch('/{job_id}/status/', response={200: JobOut, 400: ErrorOut})
def update_job_status(request, job_id: int, payload: UpdateStatus):
    job = get_object_or_404(Job, id=job_id)

    valid_statuses = ['pending', 'in_transit', 'completed', 'cancelled']
    if payload.status not in valid_statuses:
        logger.warning(f'Invalid status {payload.status} attempted on job {job_id}')
        return 400, {'detail': f'Invalid status. Must be one of: {valid_statuses}'}

    old_status = job.status
    job.status = payload.status
    job.save()

    if payload.status in ['completed', 'cancelled']:
        if job.assigned_truck:
            job.assigned_truck.status = 'available'
            job.assigned_truck.save()

    logger.info(f'Job {job_id} status changed from {old_status} to {payload.status}')
    return job