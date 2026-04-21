import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haulage.settings')
django.setup()

from core.models import Truck, Driver, Job

# Clear existing data (optional)
Truck.objects.all().delete()
Driver.objects.all().delete()
Job.objects.all().delete()

# Create Trucks
trucks = [
    Truck(plate_number="ABC 1234", model="Volvo FH16", capacity_tons=30, status="available"),
    Truck(plate_number="DEF 5678", model="Mercedes Actros", capacity_tons=25, status="available"),
    Truck(plate_number="GHJ 9012", model="MAN TGX", capacity_tons=20, status="available"),
    Truck(plate_number="KLM 3456", model="Scania R500", capacity_tons=35, status="available"),
    Truck(plate_number="NOP 7890", model="DAF XF", capacity_tons=28, status="available"),
    Truck(plate_number="QRS 1122", model="Iveco Stralis", capacity_tons=22, status="available"),
    Truck(plate_number="TUV 3344", model="Volvo FM", capacity_tons=18, status="available"),
    Truck(plate_number="WXY 5566", model="Mercedes Arocs", capacity_tons=32, status="available"),
    Truck(plate_number="ZAB 7788", model="Scania G410", capacity_tons=26, status="available"),
    Truck(plate_number="CDE 9900", model="MAN TGS", capacity_tons=24, status="available"),
]
Truck.objects.bulk_create(trucks)
print(f"Created {len(trucks)} trucks")

# Create Drivers
drivers = [
    Driver(first_name="Tendai", last_name="Moyo", license_number="ZW001234", status="available", phone="0771234567"),
    Driver(first_name="Farai", last_name="Chikwanda", license_number="ZW002345", status="available", phone="0772345678"),
    Driver(first_name="Blessing", last_name="Mutasa", license_number="ZW003456", status="available", phone="0773456789"),
    Driver(first_name="Tapiwa", last_name="Ncube", license_number="ZW004567", status="available", phone="0774567890"),
    Driver(first_name="Simba", last_name="Dube", license_number="ZW005678", status="available", phone="0775678901"),
    Driver(first_name="Rutendo", last_name="Zimba", license_number="ZW006789", status="available", phone="0776789012"),
    Driver(first_name="Tinashe", last_name="Banda", license_number="ZW007890", status="available", phone="0777890123"),
    Driver(first_name="Chiedza", last_name="Phiri", license_number="ZW008901", status="available", phone="0778901234"),
    Driver(first_name="Kudzai", last_name="Mwale", license_number="ZW009012", status="available", phone="0779012345"),
    Driver(first_name="Nyasha", last_name="Chirwa", license_number="ZW010123", status="available", phone="0770123456"),
]
Driver.objects.bulk_create(drivers)
print(f"Created {len(drivers)} drivers")

# Create Jobs
jobs = [
    Job(title="Harare to Bulawayo", origin="Harare", destination="Bulawayo", cargo_description="Construction materials", weight_tons=20, status="pending"),
    Job(title="Bulawayo to Mutare", origin="Bulawayo", destination="Mutare", cargo_description="Retail goods", weight_tons=15, status="pending"),
    Job(title="Harare to Gweru", origin="Harare", destination="Gweru", cargo_description="Agricultural equipment", weight_tons=18, status="pending"),
    Job(title="Mutare to Harare", origin="Mutare", destination="Harare", cargo_description="Timber", weight_tons=25, status="pending"),
    Job(title="Gweru to Masvingo", origin="Gweru", destination="Masvingo", cargo_description="Food supplies", weight_tons=12, status="pending"),
    Job(title="Harare to Masvingo", origin="Harare", destination="Masvingo", cargo_description="Mining equipment", weight_tons=30, status="pending"),
    Job(title="Bulawayo to Hwange", origin="Bulawayo", destination="Hwange", cargo_description="Fuel drums", weight_tons=22, status="pending"),
    Job(title="Masvingo to Mutare", origin="Masvingo", destination="Mutare", cargo_description="Cement", weight_tons=28, status="pending"),
    Job(title="Harare to Chinhoyi", origin="Harare", destination="Chinhoyi", cargo_description="Steel pipes", weight_tons=16, status="pending"),
    Job(title="Mutare to Bulawayo", origin="Mutare", destination="Bulawayo", cargo_description="Electronics", weight_tons=10, status="pending"),
]
Job.objects.bulk_create(jobs)
print(f"Created {len(jobs)} jobs")

print("Done! Seed data loaded successfully.")