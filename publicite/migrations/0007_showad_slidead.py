# Generated by Django 3.0.7 on 2025-02-27 21:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('publicite', '0006_auto_20250227_2130'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowAd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='ads/show/')),
                ('link', models.URLField(blank=True, help_text='Optional URL to redirect when clicked')),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SlideAd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='ads/slide/')),
                ('link', models.URLField(blank=True, help_text='Optional URL to redirect when clicked')),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField()),
            ],
        ),
    ]
