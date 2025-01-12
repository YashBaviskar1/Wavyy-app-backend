
from django.urls import path
from .views import CustomerView, CustomerListView

urlpatterns = [
    path('post', CustomerView.as_view()),
    path('get', CustomerListView.as_view() )
]
