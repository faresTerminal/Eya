# Generated by Django 3.0.7 on 2025-02-13 00:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_auto_20250210_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_and_outlet',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 15, 0, 19, 39, 741234, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 15, 0, 19, 39, 741234, tzinfo=utc)),
        ),
    ]
