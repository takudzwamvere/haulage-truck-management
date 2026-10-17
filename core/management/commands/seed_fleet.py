from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Driver, Truck


class Command(BaseCommand):
    help = "Seed initial fleet data (10 drivers, 10 trucks) idempotently without jobs."

    def handle(self, *args, **options):
        driver_seeds = [
            {"name": "Tendai Moyo", "license_no": "ZW10001", "phone_no": "+263770000001"},
            {"name": "Farai Chikwanda", "license_no": "ZW10002", "phone_no": "+263770000002"},
            {"name": "Blessing Mutasa", "license_no": "ZW10003", "phone_no": "+263770000003"},
            {"name": "Tapiwa Ncube", "license_no": "ZW10004", "phone_no": "+263770000004"},
            {"name": "Simba Dube", "license_no": "ZW10005", "phone_no": "+263770000005"},
            {"name": "Rutendo Zimba", "license_no": "ZW10006", "phone_no": "+263770000006"},
            {"name": "Tinashe Banda", "license_no": "ZW10007", "phone_no": "+263770000007"},
            {"name": "Chiedza Phiri", "license_no": "ZW10008", "phone_no": "+263770000008"},
            {"name": "Kudzai Mwale", "license_no": "ZW10009", "phone_no": "+263770000009"},
            {"name": "Nyasha Chirwa", "license_no": "ZW10010", "phone_no": "+263770000010"},
        ]

        truck_seeds = [
            {"registration_no": "ABC 1234", "capacity": Decimal("30.00"), "status": "available"},
            {"registration_no": "DEF 5678", "capacity": Decimal("25.00"), "status": "available"},
            {"registration_no": "GHJ 9012", "capacity": Decimal("20.00"), "status": "available"},
            {"registration_no": "KLM 3456", "capacity": Decimal("35.00"), "status": "available"},
            {"registration_no": "NOP 7890", "capacity": Decimal("28.00"), "status": "available"},
            {"registration_no": "QRS 1122", "capacity": Decimal("22.00"), "status": "available"},
            {"registration_no": "TUV 3344", "capacity": Decimal("18.00"), "status": "available"},
            {"registration_no": "WXY 5566", "capacity": Decimal("32.00"), "status": "available"},
            {"registration_no": "ZAB 7788", "capacity": Decimal("26.00"), "status": "maintenance"},
            {"registration_no": "CDE 9900", "capacity": Decimal("24.00"), "status": "maintenance"},
        ]

        drivers_created = 0
        drivers_skipped = 0
        for data in driver_seeds:
            existing = Driver.objects.filter(license_no=data["license_no"]).first()
            if existing:
                drivers_skipped += 1
            else:
                driver = Driver(
                    name=data["name"],
                    license_no=data["license_no"],
                    phone_no=data["phone_no"],
                    user=None,
                    photo=None,
                )
                driver.full_clean()
                driver.save()
                drivers_created += 1

        trucks_created = 0
        trucks_skipped = 0
        for data in truck_seeds:
            existing = Truck.objects.filter(registration_no=data["registration_no"]).first()
            if existing:
                trucks_skipped += 1
            else:
                truck = Truck(
                    registration_no=data["registration_no"],
                    capacity=data["capacity"],
                    status=data["status"],
                    photo=None,
                )
                truck.full_clean()
                truck.save()
                trucks_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Fleet seeding summary:\n"
                f"  Drivers: {drivers_created} created, {drivers_skipped} skipped\n"
                f"  Trucks: {trucks_created} created, {trucks_skipped} skipped"
            )
        )
