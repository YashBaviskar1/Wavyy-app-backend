from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse , request
from rest_framework import generics, status
from .models import Customer, Salon, Services, Booking, ServiceCategory, Coupon
from .serializers import CustomerSerializer, ServiceSerializer, SalonSerializer, BookingSerializer, ServiceCategorySerializer, SalonDetailSerializer, CouponSerializer
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
from dotenv import load_dotenv
load_dotenv()
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_ACCOUNT_AUTH_TOKEN = os.environ.get("TWILIO_ACCOUNT_AUTH_TOKEN")
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
    # account_sid = TWILIO_ACCOUNT_SID
    # auth_token = TWILIO_ACCOUNT_AUTH_TOKEN
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=f"Your Login OTP for wavvy application is {otp}. Welcome aboard!",
    #     from_="+16206788254",
    #     to=f"{phone_number}",
    # )

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
        # otp = generate_otp()
        otp = 1234
        print(otp)
        cache.set(f"otp_{phone_number}", otp, timeout=300)
        #send OTP through twilio 
        send_otp(otp, phone_number)
        return Response({"message" : "otp sent to number ", }, status=status.HTTP_200_OK)

    elif request.data["method"] == "email":
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        # Check if customer exists
        if Customer.objects.filter(email=email).exists():
            user = authenticate(request, username=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, "message": "Login successful"}, status=200)
            else:
                return Response({"error": "Invalid password"}, status=401)
        else:
            return Response({"message": "New user, proceed to signup"}, status=200)

    return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    phone_number = request.data.get("phone_number")
    otp = request.data.get("otp")
    print("hi1")
    if not phone_number or not otp:
        return Response({"error": "Phone number and OTP are required"}, status=400)
    
    cached_otp = cache.get(f"otp_{phone_number}")
    print("otp ", cached_otp)
    if cached_otp and str(cached_otp) == str(otp):
        # Check if user exists by phone_number
        print(phone_number)
        print(Customer.objects.filter(phone_number=phone_number))
        
        if Customer.objects.filter(phone_number=phone_number).exists():
            user = Customer.objects.get(phone_number=phone_number).user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=200)
        else:
            # Mark phone_number as verified for signup
            cache.set(f"verified_phone_{phone_number}", True, timeout=300)
            return Response({"message": "Proceed to signup"}, status=200)
    else:
        return Response({"error": "Invalid/expired OTP"}, status=406)


@api_view(['POST'])
def signup(request):
    method = request.data.get("method")
    if method == "phone":
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response({"error": "Phone required"}, status=400)
        
        # Check if phone exists
        if Customer.objects.filter(phone_number=phone_number).exists():
            user = Customer.objects.get(phone_number=phone_number).user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "User exists"}, status=200)
        
        # Send OTP for new user
        #otp = generate_otp()
        otp = 1234
        cache.set(f"otp_{phone_number}", otp, 300)
        send_otp(otp, phone_number)
        return Response({"message": "OTP sent"}, status=200)

    elif method == "email":
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)
        
        # Check if email exists
        if Customer.objects.filter(email=email).exists():
            user = Customer.objects.get(email=email).user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "User exists"}, status=200)
        
        # Proceed to signup
        return Response({"message": "Proceed to create user"}, status=200)



@api_view(['POST'])
def signup_create_user(request):
    # For phone signup: ensure OTP was verified
    phone_number = request.data.get("phone_number")
    if phone_number :
        if request.data.get("method") == "phone_number" : 
            if not cache.get(f"verified_phone_{phone_number}"):
                return Response({"error": "Phone not verified"}, status=400)
    
    # For email signup: ensure password is provided
    email = request.data.get("email")
    if email and not request.data.get("password"):
        return Response({"error": "Password required"}, status=400)
    
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        # Create user with email as username
        if Customer.objects.filter(phone_number=serializer.validated_data["phone_number"]).exists() :
            return Response({"message" : "Phone number already exists"}, status=401)
        user = User.objects.create_user(
            username=serializer.validated_data["phone_number"], 
            email=serializer.validated_data["email"],
            password=request.data.get("password", "123456789")
        )
        # Create customer profile
        customer = serializer.save(user=user)
        token = Token.objects.create(user=user)
        
        # Clear verification cache for phone
        if phone_number:
            cache.delete(f"verified_phone_{phone_number}")
        
        return Response({"token": token.key, "customer": serializer.data}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"passed for {}".format(request.user)})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({"message": "Logged out"}, status=200)

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
        if distance <= 1000:  
            nearby_salons.append({
                'name': salon.salon_name,
                'distance': distance
            })

    return Response(nearby_salons)

###----SERVICES----
class ServiceCategoryCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

class ServiceCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer




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
        # Fetch the salon with its related categories and services
        salon = get_object_or_404(
            Salon.objects.prefetch_related(
                'business_categories__services'  # Prefetch related service categories and services
            ),
            id=salon_id
        )

        # Serialize the salon data, including its categories and services
        serializer = SalonDetailSerializer(salon)
        return Response(serializer.data)


class SalonCreateView(generics.CreateAPIView) :
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

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
        # Validate user_id

        # Fetch customer details
        try:
            customer = Customer.objects.get(user=request.user)
            customer_serializer = CustomerSerializer(customer)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=HTTP_400_BAD_REQUEST)

        # Fetch bookings for the user
        bookings = Booking.objects.filter(user=request.user)
        booking_serializer = BookingSerializer(bookings, many=True)

        # Combine customer and booking data in the response
        response_data = {
            "customer": customer_serializer.data,
            "bookings": booking_serializer.data
        }

        return Response(response_data, status=HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


from django.utils.timezone import now
class CouponView(APIView):
 # Only authenticated users can access

    def get(self, request):
        """Fetch all active and valid coupons"""
        coupons = Coupon.objects.filter()
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        """Create a new coupon"""
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)