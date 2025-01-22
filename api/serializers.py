from rest_framework import serializers
from .models import Customer, Services, Salon, Booking

class CustomerSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Customer 
        fields = ('id', 'unique_id', 'name', 'email', 
                  'phone_number', 'date_of_birth', 
                  'created_at', 'profile_picture')
        read_only_fields = ['unique_id', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'service_name', 'service_type', 'duration_in_mins', 'price', 'category', 'rating', 'service_image']

class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = [
            'id', 'salon_name', 'owner_name', 'owner_email',
            'gst', 'salon_description', 'latitude', 'longitude',
            'profile_img'
        ]

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'salon', 'service', 'booking_date', 'appointment_date', 'status', 'total_price']
        read_only_fields = ['id', 'booking_date', 'status']