# Generated by Django 5.1.4 on 2025-01-22 22:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_services_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('appointment_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='active', max_length=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('salon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salon_bookings', to='api.salon')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_bookings', to='api.services')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
