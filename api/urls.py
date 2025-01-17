
from django.urls import path
from .views import CustomerView, CustomerListView, signup_create_user, login, test_token, verify_otp, signup

urlpatterns = [
    path('post', CustomerView.as_view()),
    path('get', CustomerListView.as_view()),
    path('auth/signup', signup),
    path('auth/signup_create_user', signup_create_user),
    path('auth/login', login),
    path('auth/verify-otp', verify_otp ),
    path('auth/test_token', test_token)

]
