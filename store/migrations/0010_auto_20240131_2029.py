# Generated by Django 3.0.7 on 2024-01-31 19:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20240131_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 19, 29, 37, 204296, tzinfo=utc)),
        ),
    ]
