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

truck_router = Router(tags=["Trucks"])
driver_router = Router(tags=["Drivers"])
job_router = Router(tags=["Jobs"])


#Trucks

@truck_router.get('/', response=list[TruckOut])
def list_trucks(request):
    return Truck.objects.all()


@truck_router.post('/', response=TruckOut)
def create_truck(request, payload: TruckIn):
    truck = Truck.objects.create(**payload.dict())
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
    return truck


@truck_router.delete('/{truck_id}/')
def delete_truck(request, truck_id: int):
    truck = get_object_or_404(Truck, id=truck_id)
    truck.delete()
    return {'success': True}


#Drivers

@driver_router.get('/', response=list[DriverOut])
def list_drivers(request):
    return Driver.objects.all()


@driver_router.post('/', response=DriverOut)
def create_driver(request, payload: DriverIn):
    driver = Driver.objects.create(**payload.dict())
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
    return driver


@driver_router.delete('/{driver_id}/')
def delete_driver(request, driver_id: int):
    driver = get_object_or_404(Driver, id=driver_id)
    driver.delete()
    return {'success': True}


#Jobs

@job_router.get('/', response=list[JobOut])
def list_jobs(request):
    return Job.objects.select_related('assigned_truck', 'assigned_driver').all()


@job_router.post('/', response=JobOut)
def create_job(request, payload: JobIn):
    job = Job.objects.create(**payload.dict())
    return job


@job_router.get('/{job_id}/', response=JobOut)
def get_job(request, job_id: int):
    return get_object_or_404(Job, id=job_id)


@job_router.delete('/{job_id}/')
def delete_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return {'success': True}


@job_router.post('/{job_id}/assign/', response={200: JobOut, 400: ErrorOut})
def assign_job(request, job_id: int, payload: AssignJob):
    job = get_object_or_404(Job, id=job_id)
    truck = get_object_or_404(Truck, id=payload.truck_id)
    driver = get_object_or_404(Driver, id=payload.driver_id)

    # business rule: truck must be available
    if truck.status != 'available':
        return 400, {'detail': f'Truck {truck.registration_no} is not available. Current status: {truck.status}'}

    # business rule: driver must not have an active job
    active_job = Job.objects.filter(
        assigned_driver=driver,
        status__in=['pending', 'in_transit']
    ).exists()
    if active_job:
        return 400, {'detail': f'Driver {driver.name} already has an active job'}

    job.assigned_truck = truck
    job.assigned_driver = driver
    job.status = 'in_transit'
    job.save()

    truck.status = 'in_transit'
    truck.save()

    return job


@job_router.patch('/{job_id}/status/', response={200: JobOut, 400: ErrorOut})
def update_job_status(request, job_id: int, payload: UpdateStatus):
    job = get_object_or_404(Job, id=job_id)

    valid_statuses = ['pending', 'in_transit', 'completed', 'cancelled']
    if payload.status not in valid_statuses:
        return 400, {'detail': f'Invalid status. Must be one of: {valid_statuses}'}

    job.status = payload.status
    job.save()

    # free up truck and driver when job is done
    if payload.status in ['completed', 'cancelled']:
        if job.assigned_truck:
            job.assigned_truck.status = 'available'
            job.assigned_truck.save()

    return job