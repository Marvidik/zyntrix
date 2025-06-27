from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.dateparse import parse_datetime
from user.models import UserProfile,Otp,Bonus
from .utils import send_welcome_mail ,generate_numeric_otp, send_otp_mail,process_referral
from django.contrib.auth import authenticate
from django.utils.timezone import now
from user.utils import update_user_account  




@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  
@permission_classes([AllowAny])  # allow public registration
def register_user(request):
    try:
        data = request.data

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        phone = data.get('phone')
        country = data.get('country')
        account_type = data.get('account_type')
        dob = data.get('dob')  # ISO format
        address = data.get('address')
        referal_id=data.get('referal_id')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        



        # Core user creation in atomic block
        with transaction.atomic():
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                country=country,
                account_type=account_type,
                dob=parse_datetime(dob) if dob else None,
                address=address
            )
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)

            # ✅ Send welcome mail
            send_welcome_mail(
                email=email,
                full_name=full_name,
                username=username,
                account_type=account_type,
                user_id=user.id
            )
        # Process referral if provided
        process_referral(referal_id, user)

        return Response({
            'message': 'User registered successfully',
            'token': token.key,
            'user': {
                'id':user.id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'phone': phone,
                'country': country,
                'account_type': account_type,
                'dob': dob,
                'address': address
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=403)

    if not user.check_password(password):
        return Response({'error': 'Invalid email or password'}, status=403)
    
    userprofile=UserProfile.objects.get(user=user)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        
        'id':user.id,
        'token': token.key,
        'username': user.username,
        'email': user.email,
        'full_name':userprofile.full_name,
        'status':userprofile.status,
        'kyc':userprofile.kyc,
        'phone':userprofile.phone,
        'country':userprofile.country,
        'account_type':userprofile.account_type,
        'dob':userprofile.dob,
        'address':userprofile.address 

    })


@api_view(['GET'])
@authentication_classes([])  # Disable auth for public access
@permission_classes([AllowAny])
@transaction.atomic 
def verify_account(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = UserProfile.objects.get(user=user)

        if not Bonus.objects.filter(user=user, type="reg bonus").exists():
            Bonus.objects.create(
                user=user,
                amount=5,  
                type="reg bonus",
                date=now()
            )
        update_user_account(user) 

        if profile.status == "Verified":
            return Response({'message': 'Account already verified'}, status=200)

        profile.status = "Verified"
        profile.save()

        

        return Response({'message': 'Account verified successfully'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=404)
    



@api_view(['POST'])
@permission_classes([])
def request_otp(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=404)

    otp = generate_numeric_otp()

    Otp.objects.update_or_create(user=user, defaults={'otp': otp})
    send_otp_mail(user.email, otp)

    return Response({
        'message': 'OTP sent successfully',
    }, status=200)

@api_view(['POST'])
@authentication_classes([])  # no auth needed
@permission_classes([AllowAny])  # public access
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'error': 'Email and OTP are required'}, status=400)

    try:
        user = User.objects.get(email=email)
        user_otp = Otp.objects.get(user=user)

        if str(user_otp.otp) != str(otp):
            return Response({'error': 'Invalid OTP'}, status=403)

        return Response({'message': 'OTP verified successfully'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Otp.DoesNotExist:
        return Response({'error': 'OTP not found for this user'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Old and new passwords are required'}, status=400)

    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=403)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=200)


@api_view(['POST'])
@authentication_classes([])  # No session/token auth
@permission_classes([AllowAny])  # Public access
def reset_password_by_email(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'error': 'Email and new password are required'}, status=400)

    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=404)