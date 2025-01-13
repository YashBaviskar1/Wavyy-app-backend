from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Customer 
        fields = ('id', 'unique_id', 'name', 'email', 
                  'phone_number', 'date_of_birth', 
                  'created_at', 'profile_picture')
        