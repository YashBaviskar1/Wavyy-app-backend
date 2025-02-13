from django.db import models
import random 
import string 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
def generate_unique_id():
    length = 8
    while True:
        unique_id = ''.join(random.choices(string.ascii_uppercase, k=length))
        if not Customer.objects.filter(unique_id=unique_id).exists():
            return unique_id 

def validate_image_size(file):
    max_size = 2 * 1024 * 1024  # 2 MB
    if file.size > max_size:
        raise ValidationError("File size exceeds the 2 MB limit.")
# Create your models here.
class Customer(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    unique_id = models.CharField(max_length= 10, default=generate_unique_id, unique=True)
    name = models.CharField(max_length=50, null=False)
    gender = models.CharField(max_length=10, null=False)
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
    address_description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    profile_img = models.ImageField(upload_to="profiles/", null=True, blank=True, validators=[validate_image_size])
    is_featured = models.BooleanField(default=False) 
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
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="salon_bookings")
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name="service_bookings")
    booking_date = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking {self.id} for {self.user.username} at {self.salon.salon_name}"



def generate_unique_coupon_id():
    length = 10
    while True:
        unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Coupon.objects.filter(coupon_id=unique_id).exists():
            return unique_id

class Coupon(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Name of the coupon
    coupon_id = models.CharField(max_length=20, unique=True, default=generate_unique_coupon_id)  # Unique coupon ID
    description = models.CharField(max_length=200)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Fixed discount price
    discount_percentage = models.FloatField(null=True, blank=True)  # Percentage discount
    valid_from = models.DateTimeField()  
    valid_to = models.DateTimeField()  
    is_active = models.BooleanField(default=True)  # Coupon status (Active/Inactive)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  
    used_count = models.PositiveIntegerField(default=0) 
    applicable_services = models.ManyToManyField(Services, blank=True, related_name="applicable_coupons")  # Applicable services
    applicable_salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="salon_coupons", null=True, blank=True)  # Restrict to a specific salon (if needed)

    def __str__(self):
        return f"{self.name} ({self.coupon_id})"

    def is_valid(self):
        """Check if the coupon is valid based on dates and usage."""
        from django.utils.timezone import now
        if not self.is_active:
            return False
        if self.valid_from > now() or self.valid_to < now():
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True


## BOOKMARKS 
class Bookmark(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookmarks')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'salon')  # Prevent duplicate bookmarks

    def __str__(self):
        return f"{self.user.name} bookmarked {self.salon.salon_name}"