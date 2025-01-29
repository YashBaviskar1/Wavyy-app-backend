from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse , request
from rest_framework import generics, status
from .models import Customer, Salon, Services, Booking
from .serializers import CustomerSerializer, ServiceSerializer, SalonSerializer, BookingSerializer
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from .serializers import CustomerSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.db.models import Q
import time
import random 
from twilio.rest import Client
import os 
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import math
class CustomerView(generics.CreateAPIView) :
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerListView(generics.ListAPIView) : 
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# PROFILE VIEW
class CustomerProfileView(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            # Fetch the profile for the authenticated user
            return self.request.user.customer_profile
        except Customer.DoesNotExist:
            # If no profile exists for the user, raise a custom 404 error
            raise NotFound(detail="Profile Not Found")
# PROFILE UPDATE 

class CustomerProfileUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        try:
            return self.request.user.customer_profile
        except Customer.DoesNotExist:
            raise NotFound(detail="Profile Not Found")
# PROFILE UPDATE 

from rest_framework.generics import DestroyAPIView

# PROFILE DELETE


class CustomerProfileDeleteView(DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        try:
            return self.request.user.customer_profile
        except Customer.DoesNotExist:
            raise NotFound(detail="Profile Not Found")
def generate_otp() : 
    return random.randint(1000, 9999)

def send_otp(otp, phone_number) : 
    account_sid = "TWILIO_ACCOUNT_SID"
    auth_token = "TWILIO_AUTH_TOKEN"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body="Your Login OTP for wavvy application is {otp}. Welcome aboard!",
        from_="+16206788254 ",
        to=f"{phone_number}",
    )

    # print(message.body)
    print(f"{otp} sent to number {phone_number}")

def user_exists(phone_number = None, email = None):
    return Customer.objects.filter(phone_number=phone_number).exists() or Customer.objects.filter(email=email).exists()

#TO CALCUATE DISTANCE 
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c  
    return distance




@api_view(['POST']) 
def login(request):
    if request.data["method"] == "phone" :
        phone_number = request.data["phone_number"]
        if not phone_number : 
            return Response({"error" : "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        #GENERATE 4 DIGIT OTP CODE 
        otp = generate_otp()
        print(otp)
        cache.set(f"otp_{phone_number}", otp, timeout=300)
        #send OTP through twilio 
        send_otp(otp, phone_number)
        return Response({"message" : "otp sent to number ", }, status=status.HTTP_200_OK)

    elif request.data["method"] == "email":
        email = request.data.get("email")
        password = request.data.get("password")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if user_exists(email=email):
            # Custom authentication using email
            user = authenticate(request, username=email, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({"message": "New User, Sign up"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    phone_number = request.data.get("phone_number")
    otp = request.data.get("otp")
    if not phone_number or not otp:
        return Response({"error": "Phone number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
    cached_otp = cache.get(f"otp_{phone_number}")
    if cached_otp and str(cached_otp) == str(otp):
        if user_exists(phone_number=phone_number) :
            return Response({"message": "Verification successful"}, status=status.HTTP_202_ACCEPTED)
        else : 
            return Response({"message" : "New User, proceed to signup"})
    else:
        return Response({"message": "Incorrect or expired OTP"}, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST'])
def signup(request) :
    if request.data["method"] == "phone" :
        phone_number = request.data["phone_number"]
        if not phone_number :
            return Response({"error" : "phone_number is required "}, status=status.HTTP_400_BAD_REQUEST)
        if user_exists(phone_number=phone_number) :
            user = User.objects.filter(customer_profile__phone_number=phone_number).first()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"message": "User already exists, logged in", "token": token.key},
                status=status.HTTP_200_OK
            )
        otp = generate_otp()
        print(otp)
        cache.set(f"otp_{phone_number}", otp, timeout=300)
        #send OTP through twilio 
        send_otp(otp, phone_number)
        return Response({"message" : "otp sent to number ", }, status=status.HTTP_200_OK)  
    elif request.data["method"] == "email" : 
        email = request.data["email"]
        password = request.data["password"]
        if not email :
            return Response({"error" : "email is required "}, status=status.HTTP_400_BAD_REQUEST)   
        if not password : 
            return Response({"error" : "password is required "}, status=status.HTTP_400_BAD_REQUEST)   
        if user_exists(email=email) :
            user = User.objects.filter(customer_profile__email__iexact=email).first()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"message": "User already exists, logged in", "token": token.key},
                status=status.HTTP_200_OK
            )
        return Response({"email" : email, "password" : password, "message" : "new user proceed to signup"}, status=status.HTTP_200_OK)


@api_view(['POST']) 
def signup_create_user(request):
    serializer = CustomerSerializer(data = request.data)
    if serializer.is_valid() :
        user = User.objects.create_user(
            username= request.data["name"] + str(random.randint(0, 9999)),
            email=request.data["email"],
            password=request.data.get('password', '')
        )
        customer = serializer.save(user=user)
        token = Token.objects.create(user=user)
        return Response({"token" : token.key, "customer" : serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"passed for {}".format(request.user)})



### -----LOCATION API-------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_salons_by_location(request):
    latitude = float(request.query_params.get('latitude'))
    longitude = float(request.query_params.get('longitude'))
    
    salons = Salon.objects.all()
    nearby_salons = []

    for salon in salons:
        distance = haversine(latitude, longitude, salon.latitude, salon.longitude)
        if distance <= 10:  
            nearby_salons.append({
                'name': salon.name,
                'address': salon.address,
                'distance': distance
            })

    return Response(nearby_salons)

###----SERVICES----

class ServiceFilterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category = request.query_params.get('category')
        price_min = request.query_params.get('priceMin')
        price_max = request.query_params.get('priceMax')
        rating = request.query_params.get('rating')

        filters = Q()

        if category:
            filters &= Q(category__name__icontains=category)
        if price_min:
            filters &= Q(price__gte=price_min)
        if price_max:
            filters &= Q(price__lte=price_max)
        if rating:
            filters &= Q(rating__gte=rating)

        services = Services.objects.filter(filters)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)
    

###SALON DETAILS API 

class SalonDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, salon_id):
        salon = get_object_or_404(Salon, id=salon_id)
        serializer = SalonSerializer(salon)
        return Response(serializer.data)

# View for fetching services for a salon
class SalonServicesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, salon_id):
        salon = get_object_or_404(Salon, id=salon_id)
        services = salon.business_services.all() 
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)



## BOOKING HANDLING 


# POST /bookings/create
class BookingCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        salon_id = request.data.get('salon_id')
        service_id = request.data.get('service_id')
        appointment_date = request.data.get('appointment_date')

        # Validate input
        if not salon_id or not service_id or not appointment_date:
            return Response({"error": "salon_id, service_id, and appointment_date are required."}, status=HTTP_400_BAD_REQUEST)

        salon = get_object_or_404(Salon, id=salon_id)
        service = get_object_or_404(Services, id=service_id)

        # Create booking
        booking = Booking.objects.create(
            user=user,
            salon=salon,
            service=service,
            appointment_date=appointment_date,
            total_price=service.price
        )
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=HTTP_201_CREATED)

# DELETE /bookings/{bookingId}/cancel
class BookingCancelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if booking.status == "completed":
            return Response({"error": "Cannot cancel a completed booking."}, status=HTTP_400_BAD_REQUEST)

        booking.status = "canceled"
        booking.save()
        return Response({"message": "Booking canceled successfully."}, status=HTTP_200_OK)

# GET /bookings/status?userId={userId}
class BookingStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('userId')
        if not user_id or int(user_id) != request.user.id:
            return Response({"error": "Invalid or unauthorized userId."}, status=HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=HTTP_200_OK)