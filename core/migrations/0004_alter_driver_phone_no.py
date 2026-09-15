from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_job_status_alter_truck_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='phone_no',
            field=models.CharField(
                max_length=20,
                validators=[
                    RegexValidator(
                        regex=r'^\+?[0-9\s\-]+$',
                        message='Only numbers',
                    )
                ],
            ),
        ),
    ]
