# Generated by Django 3.0.7 on 2024-01-26 09:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20240126_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 28, 9, 44, 42, 195500, tzinfo=utc)),
        ),
    ]
