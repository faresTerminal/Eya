# Generated by Django 3.0.7 on 2023-12-03 21:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='initial_stock_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='variation',
            name='reorder_point',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 5, 21, 22, 49, 343298, tzinfo=utc)),
        ),
    ]