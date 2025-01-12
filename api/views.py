from django.shortcuts import render
from django.http import HttpResponse , request
from rest_framework import generics
from .models import Customer
from .serializers import CustomerSerializer

class CustomerView(generics.CreateAPIView) :
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerListView(generics.ListAPIView) : 
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
