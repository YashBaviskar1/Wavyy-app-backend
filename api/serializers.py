from rest_framework import serializers
from .models import Customer, Services, Salon, Booking, ServiceCategory

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
        fields = ['id', 'business', 'service_name', 'service_type', 'duration_in_mins', 'price', 'category', 'rating', 'service_image']

class ServiceCategorySerializer(serializers.ModelSerializer) :
    services = ServiceSerializer(many=True, read_only=True)
    class Meta :
        model = ServiceCategory
        fields = ['id', 'business', 'name', 'description', 'parent', 'services']



class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = [
            'id', 'salon_name', 'phone_number', 'owner_name', 'owner_email',
            'gst', 'salon_description', 'latitude', 'longitude',
            'profile_img'
        ]

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'salon', 'service', 'booking_date', 'appointment_date', 'status', 'total_price']
        read_only_fields = ['id', 'booking_date', 'status']


class SalonDetailSerializer(serializers.ModelSerializer):
    business_categories = ServiceCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Salon
        fields = [
            'id', 'salon_name', 'owner_name', 'owner_email', 'gst',
            'salon_description', 'latitude', 'longitude', 'profile_img',
            'business_categories'
        ]

from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"  # Include all fields in the response
