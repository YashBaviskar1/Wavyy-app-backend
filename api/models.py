from django.db import models
import random 
import string 
from django.contrib.auth.models import User
def generate_unique_id() : 
    length = 8
    while True :
        unique_id = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Customer.objects.filter(unique_id = unique_id).count() == 0 :
            break
    return unique_id
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


