import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haulage.settings')
django.setup()

from core.models import Truck, Driver, Job


def validated_create(model_class, **kwargs):
    """Create a model instance running full model validation before saving."""
    obj = model_class(**kwargs)
    obj.full_clean()
    obj.save()
    return obj


Truck.objects.all().delete()
Driver.objects.all().delete()
Job.objects.all().delete()

truck_data = [
    dict(registration_no="ABC 1234", capacity=30, status="available"),
    dict(registration_no="DEF 5678", capacity=25, status="available"),
    dict(registration_no="GHJ 9012", capacity=20, status="available"),
    dict(registration_no="KLM 3456", capacity=35, status="available"),
    dict(registration_no="NOP 7890", capacity=28, status="available"),
    dict(registration_no="QRS 1122", capacity=22, status="available"),
    dict(registration_no="TUV 3344", capacity=18, status="available"),
    dict(registration_no="WXY 5566", capacity=32, status="available"),
    dict(registration_no="ZAB 7788", capacity=26, status="available"),
    dict(registration_no="CDE 9900", capacity=24, status="available"),
]
trucks = [validated_create(Truck, **d) for d in truck_data]
print(f"Created {len(trucks)} trucks")

driver_data = [
    dict(name="Tendai Moyo",      license_no="ZW001234", phone_no="0771234567"),
    dict(name="Farai Chikwanda",  license_no="ZW002345", phone_no="0772345678"),
    dict(name="Blessing Mutasa",  license_no="ZW003456", phone_no="0773456789"),
    dict(name="Tapiwa Ncube",     license_no="ZW004567", phone_no="0774567890"),
    dict(name="Simba Dube",       license_no="ZW005678", phone_no="0775678901"),
    dict(name="Rutendo Zimba",    license_no="ZW006789", phone_no="0776789012"),
    dict(name="Tinashe Banda",    license_no="ZW007890", phone_no="0777890123"),
    dict(name="Chiedza Phiri",    license_no="ZW008901", phone_no="0778901234"),
    dict(name="Kudzai Mwale",     license_no="ZW009012", phone_no="0779012345"),
    dict(name="Nyasha Chirwa",    license_no="ZW010123", phone_no="0770123456"),
]
drivers = [validated_create(Driver, **d) for d in driver_data]
print(f"Created {len(drivers)} drivers")

job_data = [
    dict(pick_up_location="Harare",   delivery_location="Bulawayo", cargo="Construction materials", status="pending"),
    dict(pick_up_location="Bulawayo", delivery_location="Mutare",   cargo="Retail goods",           status="pending"),
    dict(pick_up_location="Harare",   delivery_location="Gweru",    cargo="Agricultural equipment", status="in_transit"),
    dict(pick_up_location="Mutare",   delivery_location="Harare",   cargo="Timber",                 status="pending"),
    dict(pick_up_location="Gweru",    delivery_location="Masvingo", cargo="Food supplies",          status="completed"),
    dict(pick_up_location="Harare",   delivery_location="Masvingo", cargo="Mining equipment",       status="pending"),
    dict(pick_up_location="Bulawayo", delivery_location="Hwange",   cargo="Fuel drums",             status="in_transit"),
    dict(pick_up_location="Masvingo", delivery_location="Mutare",   cargo="Cement",                 status="pending"),
    dict(pick_up_location="Harare",   delivery_location="Chinhoyi", cargo="Steel pipes",            status="completed"),
    dict(pick_up_location="Mutare",   delivery_location="Bulawayo", cargo="Electronics",            status="pending"),
]
jobs = [validated_create(Job, **d) for d in job_data]
print(f"Created {len(jobs)} jobs")

print("Done! Seed data loaded successfully.")