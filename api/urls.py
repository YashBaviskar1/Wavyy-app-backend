
from django.urls import path
from .views import CustomerView, CustomerListView, signup_create_user, login, test_token, verify_otp, signup
from .views import CustomerProfileView, CustomerProfileUpdateView, CustomerProfileDeleteView, get_salons_by_location, ServiceFilterView
from .views import SalonDetailView, SalonServicesView, BookingCreateView, BookingStatusView, BookingCancelView, SalonCreateView, ServiceCreateView
from .views import ServiceCategoryCreateView, CouponView, BookingsListView, SalonCategoryFilterView, FeaturedSalonListView, BookmarkedSalonsView, BookmarkView
from django.conf import settings
from django.conf.urls.static import static
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
    path('bookings/create', BookingCreateView.as_view(), name='create_booking'),
    path('bookings/<int:booking_id>/cancel', BookingCancelView.as_view(), name='cancel_booking'),
    path('bookings/status', BookingStatusView.as_view(), name='booking_status'),
    path('bookmarks', BookmarkView.as_view(), name='manage-bookmarks'),
    path('bookmarks/list', BookmarkedSalonsView.as_view(), name='bookmarked-salons'),
    path('all_bookings', BookingsListView.as_view()),
    path('featured-salons/', FeaturedSalonListView.as_view(), name='featured-salons'),
    path('create_salons', SalonCreateView.as_view(), name = 'salon-create'),
    path('create_service', ServiceCreateView.as_view(), name='create_service'),
    path('service_categories',  ServiceCategoryCreateView.as_view(), name='create-service-category'),
    path('salons/filter/', SalonCategoryFilterView.as_view(), name='salon-filter'),
    path('coupons/', CouponView.as_view(), name='coupons-list'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)