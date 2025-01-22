from django.shortcuts import render
from django.http import HttpResponse , request
from rest_framework import generics, status
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth import authenticate
import time
import random 
from twilio.rest import Client
import os 
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
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