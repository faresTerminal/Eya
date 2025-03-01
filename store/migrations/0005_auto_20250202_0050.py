# Generated by Django 3.0.7 on 2025-02-01 23:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20250202_0040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='affiliatecommission',
            name='affiliate',
        ),
        migrations.RemoveField(
            model_name='affiliatecommission',
            name='order',
        ),
        migrations.RemoveField(
            model_name='affiliatereferral',
            name='affiliate',
        ),
        migrations.RemoveField(
            model_name='affiliatereferral',
            name='referred_user',
        ),
        migrations.AlterField(
            model_name='daily_and_outlet',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 3, 23, 50, 27, 993556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 3, 23, 50, 27, 992555, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='Affiliate',
        ),
        migrations.DeleteModel(
            name='AffiliateCommission',
        ),
        migrations.DeleteModel(
            name='AffiliateReferral',
        ),
    ]
