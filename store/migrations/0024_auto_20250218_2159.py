# Generated by Django 3.0.7 on 2025-02-18 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_auto_20250218_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_and_outlet',
            name='image_slide',
            field=models.ImageField(upload_to='photos/deals-and-outlet'),
        ),
        migrations.AlterField(
            model_name='daily_slide',
            name='expiration_time',
            field=models.DateTimeField(),
        ),
    ]
