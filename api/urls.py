
from django.urls import path
from .views import CustomerView, CustomerListView, signup_create_user, login, test_token, verify_otp, signup
from .views import CustomerProfileView, CustomerProfileUpdateView, CustomerProfileDeleteView, get_salons_by_location, ServiceFilterView
from .views import SalonDetailView, SalonServicesView
urlpatterns = [
    path('post', CustomerView.as_view()),
    path('get', CustomerListView.as_view()),
    path('auth/signup', signup),
    path('auth/signup_create_user', signup_create_user),
    path('auth/login', login),
    path('auth/verify-otp', verify_otp ),
    path('auth/test_token', test_token),
    path('profile/view', CustomerProfileView.as_view(), name='view-profile'),
    path('profile/update', CustomerProfileUpdateView.as_view(), name='update-profile'),
    path('profile/delete', CustomerProfileDeleteView.as_view(), name='delete-profile'),
    path('salons', get_salons_by_location, name='get_salons_by_location'),
    path('services/filter', ServiceFilterView.as_view(), name='service_filter'),
    path('salons/<int:salon_id>', SalonDetailView.as_view(), name='salon_detail'),
    path('salons/<int:salon_id>/services', SalonServicesView.as_view(), name='salon_services'),
]