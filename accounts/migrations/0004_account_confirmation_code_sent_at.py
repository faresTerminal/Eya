# Generated by Django 3.0.7 on 2025-02-28 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20250228_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='confirmation_code_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
