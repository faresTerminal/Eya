# Generated by Django 3.0.7 on 2025-02-02 20:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20250202_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_and_outlet',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 4, 20, 43, 59, 401329, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 4, 20, 43, 59, 385703, tzinfo=utc)),
        ),
    ]
