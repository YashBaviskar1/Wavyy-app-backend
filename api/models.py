from django.db import models
import random 
import string 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
def generate_unique_id() : 
    length = 8
    while True :
        unique_id = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Customer.objects.filter(unique_id = unique_id).count() == 0 :
            break
    return unique_id

def validate_image_size(file):
    max_size = 2 * 1024 * 1024  # 2 MB
    if file.size > max_size:
        raise ValidationError("File size exceeds the 2 MB limit.")
# Create your models here.
class Customer(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    unique_id = models.CharField(max_length= 10, default="", unique=True)
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(null=False)
    phone_number = models.CharField(max_length=15, null=False)
    date_of_birth = models.DateField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True) 



#FROM SAAS DATA WILL COME ->

class Salon(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=100)
    salon_name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    gst = models.CharField(max_length=15, blank=True, null=True)
    salon_description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    profile_img = models.ImageField(upload_to="profiles/", null=True, blank=True, validators=[validate_image_size])

    def __str__(self):
        return self.salon_name
    

class ServiceCategory(models.Model):
    business = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='business_categories')
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True, max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

class Services(models.Model):
    business = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='business_services')
    service_name = models.CharField(max_length=50)
    service_type = models.CharField(
        max_length=50,
        choices=[("Basic", "Basic"), ("Premium", "Premium"), ("Add-on", "Add-on")]
    )
    duration_in_mins = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="services")
    service_image = models.ImageField(upload_to="services-images/", null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.service_name
    
class Packages(models.Model):
    business = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='business_packages')
    package_name = models.CharField(max_length=50)
    package_duration_in_mins = models.PositiveIntegerField()
    package_price = models.PositiveIntegerField()

    def __str__(self):
        return self.package_name