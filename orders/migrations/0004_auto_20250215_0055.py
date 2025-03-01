# Generated by Django 3.0.7 on 2025-02-14 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_purchased_through_affiliate'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='download_expiration',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
