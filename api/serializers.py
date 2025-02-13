from rest_framework import serializers
from .models import Customer, Services, Salon, Booking, ServiceCategory, Bookmark
from django.db.models import Q, Avg



class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'salon', 'created_at']
        read_only_fields = ['id', 'created_at']

class CustomerSerializer(serializers.ModelSerializer):
    bookmarks = BookmarkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Customer 
        fields = ('id', 'unique_id', 'name', 'gender', 'email', 
                  'phone_number', 'date_of_birth', 'created_at', 
                  'profile_picture', 'bookmarks')
        read_only_fields = ['unique_id', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Services
        fields = ['id', 'business', 'service_name', 'service_type', 'duration_in_mins', 'price', 'category', 'rating', 'service_image']
    def validate(self, data):
        # Ensure category's business matches the service's business
        if data['category'].business != data['business']:
            raise serializers.ValidationError(
                "Category does not belong to the selected salon."
            )
        return data
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
            'gst', 'salon_description', 'latitude', 'longitude', "address_description", "is_featured",
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

from django.db.models import Q, Avg
from rest_framework import serializers
from .models import Salon, Services  # Ensure these models are correctly imported
from .serializers import ServiceSerializer  # Ensure ServiceSerializer is imported

class SalonFilterSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()  # Calculate average rating from services

    class Meta:
        model = Salon
        fields = ['id', 'salon_name', 'address', 'rating', 'services', 'is_featured']
        
    def get_address(self, obj):
        # Use address from your model (assuming it's named `address`, not `address_description`)
        return obj.address_description if obj.address_description else "Address not available"
        
    def get_rating(self, obj):
        # Calculate average rating from all services in this salon
        avg_rating = Services.objects.filter(
            business=obj  # Ensure "business" is the correct foreign key
        ).aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else None
        
    def get_services(self, obj):
        category_name = self.context.get('category', '').strip()  # Ensure category_name is not None
        if not category_name:
            return []  # Return an empty list if no category is provided

        services = Services.objects.filter(
            business=obj  # Assuming "business" is the correct relation to Salon
        ).filter(
            Q(category__name__icontains=category_name) | Q(service_name__icontains=category_name)
        )

        return ServiceSerializer(services, many=True).data
