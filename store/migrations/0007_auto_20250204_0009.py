# Generated by Django 3.0.7 on 2025-02-03 23:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20250202_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_and_outlet',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 5, 23, 9, 12, 764583, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 5, 23, 9, 12, 764583, tzinfo=utc)),
        ),
    ]
