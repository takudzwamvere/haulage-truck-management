import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haulage.settings')
django.setup()

from core.models import Truck, Driver, Job

Truck.objects.all().delete()
Driver.objects.all().delete()
Job.objects.all().delete()

trucks = Truck.objects.bulk_create([
    Truck(registration_no="ABC 1234", capacity=30, status="available"),
    Truck(registration_no="DEF 5678", capacity=25, status="available"),
    Truck(registration_no="GHJ 9012", capacity=20, status="available"),
    Truck(registration_no="KLM 3456", capacity=35, status="available"),
    Truck(registration_no="NOP 7890", capacity=28, status="available"),
    Truck(registration_no="QRS 1122", capacity=22, status="available"),
    Truck(registration_no="TUV 3344", capacity=18, status="available"),
    Truck(registration_no="WXY 5566", capacity=32, status="available"),
    Truck(registration_no="ZAB 7788", capacity=26, status="available"),
    Truck(registration_no="CDE 9900", capacity=24, status="available"),
])
print(f"Created {len(trucks)} trucks")

drivers = Driver.objects.bulk_create([
    Driver(name="Tendai Moyo", license_no="ZW001234", phone_no="0771234567"),
    Driver(name="Farai Chikwanda", license_no="ZW002345", phone_no="0772345678"),
    Driver(name="Blessing Mutasa", license_no="ZW003456", phone_no="0773456789"),
    Driver(name="Tapiwa Ncube", license_no="ZW004567", phone_no="0774567890"),
    Driver(name="Simba Dube", license_no="ZW005678", phone_no="0775678901"),
    Driver(name="Rutendo Zimba", license_no="ZW006789", phone_no="0776789012"),
    Driver(name="Tinashe Banda", license_no="ZW007890", phone_no="0777890123"),
    Driver(name="Chiedza Phiri", license_no="ZW008901", phone_no="0778901234"),
    Driver(name="Kudzai Mwale", license_no="ZW009012", phone_no="0779012345"),
    Driver(name="Nyasha Chirwa", license_no="ZW010123", phone_no="0770123456"),
])
print(f"Created {len(drivers)} drivers")

jobs = Job.objects.bulk_create([
    Job(pick_up_location="Harare", delivery_location="Bulawayo", cargo="Construction materials", status="pending"),
    Job(pick_up_location="Bulawayo", delivery_location="Mutare", cargo="Retail goods", status="pending"),
    Job(pick_up_location="Harare", delivery_location="Gweru", cargo="Agricultural equipment", status="in_transit"),
    Job(pick_up_location="Mutare", delivery_location="Harare", cargo="Timber", status="pending"),
    Job(pick_up_location="Gweru", delivery_location="Masvingo", cargo="Food supplies", status="completed"),
    Job(pick_up_location="Harare", delivery_location="Masvingo", cargo="Mining equipment", status="pending"),
    Job(pick_up_location="Bulawayo", delivery_location="Hwange", cargo="Fuel drums", status="in_transit"),
    Job(pick_up_location="Masvingo", delivery_location="Mutare", cargo="Cement", status="pending"),
    Job(pick_up_location="Harare", delivery_location="Chinhoyi", cargo="Steel pipes", status="completed"),
    Job(pick_up_location="Mutare", delivery_location="Bulawayo", cargo="Electronics", status="pending"),
])
print(f"Created {len(jobs)} jobs")

print("Done! Seed data loaded successfully.")