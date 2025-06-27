from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user.models import UserAccount, Deposit, Profit, Bonus, ReferalBonus,Withdrawal,ReferalList,UserProfile,WithdrawalInfo,OtherSettings,UserInvestment,KYCVerification
from .utils import update_user_account,send_deposit_mail,process_matured_investments, send_withdrawal_mail
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.dateparse import parse_date
from .serializers import WithdrawalInfoSerializer,OtherSettingsSerializer, DepositSerializer, WithdrawalSerializer, UserInvestmentSerializer,UserListInvestmentSerializer, KYCSerializer
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from .decorators import kyc_required


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_info(request):
    update_user_account(request.user)
    process_matured_investments()  
    try:
        account = UserAccount.objects.get(user=request.user)
        data = {
            "account_balance": account.account_balance,
            "total_profit": account.total_profit,
            "bonus": account.bonus,
            "referal_bonus": account.referal_bonus,
            "total_deposit": account.total_deposit,
            "total_withdrawal": account.total_withdrawal
        }
        return Response(data, status=200)
    except UserAccount.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    user = request.user

    # Collect and normalize each model's data
    deposits = Deposit.objects.filter(user=user).values('amount', 'type', 'date')
    bonuses = Bonus.objects.filter(user=user).values('amount', 'type', 'date')
    referals = ReferalBonus.objects.filter(user=user).values('amount', 'type', 'date')
    withdrawals = Withdrawal.objects.filter(user=user).values('amount', 'type', 'date')
    profits = Profit.objects.filter(user=user).values('amount', 'type', 'date')

    # Merge all into one list
    history = list(deposits) + list(bonuses) + list(referals) + list(withdrawals) + list(profits)

    # Sort by date descending
    sorted_history = sorted(history, key=lambda x: x['date'], reverse=True)

    return Response({'history': sorted_history})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # For handling form-data with files
def create_deposit(request):
    try:
        user = request.user
        amount = request.data.get('amount')
        coin = request.data.get('coin')
        proof = request.FILES.get('proof')

        if not all([amount, coin, proof]):
            return Response({'error': 'All fields (amount, coin, proof) are required.'}, status=400)

        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            coin=coin,
            proof=proof
        )
        send_deposit_mail(
                email=user.email,
                amount=amount
            )

        return Response({'message': 'Deposit submitted successfully.'}, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profits(request):
    user = request.user
    profits = Profit.objects.filter(user=user).order_by('-date')

    data = [
        {
            'amount': p.amount,
            'plan': p.plan,
            'type': p.type,
            'date': p.date
        }
        for p in profits
    ]

    return Response({'profits': data}, status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referal_list(request):
    referals = ReferalList.objects.all().order_by('-date_registered')

    data = [
        {
            'client_name': r.client_name,
            'ref_level': r.ref_level,
            'client_status': r.client_status,
            'date_registered': r.date_registered
        }
        for r in referals
    ]

    return Response({'referals': data}, status=200)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)

    data = request.data

    # Update User model field
    if 'email' in data:
        user.email = data['email']
        user.save()

    # Update UserProfile model fields
    profile.full_name = data.get('full_name', profile.full_name)
    profile.phone = data.get('phone', profile.phone)
    profile.country = data.get('country', profile.country)
    profile.address = data.get('address', profile.address)

    if 'dob' in data:
        parsed_dob = parse_date(data['dob'])  # expects format like 'YYYY-MM-DD'
        if parsed_dob:
            profile.dob = parsed_dob

    profile.save()

    return Response({'message': 'Profile updated successfully'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_withdrawal_info(request):
    user = request.user
    data = request.data

    try:
        withdrawal_info = WithdrawalInfo.objects.get(user=user)
        serializer = WithdrawalInfoSerializer(withdrawal_info, data=data)
    except WithdrawalInfo.DoesNotExist:
        # Inject user ID when creating
        serializer = WithdrawalInfoSerializer(data={**data, 'user': user.id})

    if serializer.is_valid():
        serializer.save(user=user)  # Pass user explicitly to avoid NULL error
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_withdrawal_info(request):
    user = request.user
    try:
        withdrawal_info = WithdrawalInfo.objects.get(user=user)
        serializer = WithdrawalInfoSerializer(withdrawal_info)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except WithdrawalInfo.DoesNotExist:
        return Response({}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_other_settings(request):
    user = request.user
    data = request.data

    try:
        settings = OtherSettings.objects.get(user=user)
        serializer = OtherSettingsSerializer(settings, data=data)
    except OtherSettings.DoesNotExist:
        serializer = OtherSettingsSerializer(data={**data, 'user': user.id})

    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_other_settings(request):
    settings, created = OtherSettings.objects.get_or_create(user=request.user)
    serializer = OtherSettingsSerializer(settings)
    return Response(serializer.data)

    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@kyc_required
def transfer_funds(request):
    sender = request.user
    recipient_identifier = request.data.get('recipient')  # email or username
    amount = request.data.get('amount')
    password = request.data.get('password')

    # Validate input
    if not recipient_identifier or not amount or not password:
        return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = int(amount)
    except ValueError:
        return Response({"detail": "Amount must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    if amount <= 0:
        return Response({"detail": "Amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate password
    if not sender.check_password(password):
        return Response({"detail": "Invalid password."}, status=status.HTTP_403_FORBIDDEN)

    # Find recipient by username or email
    try:
        recipient = User.objects.get(username=recipient_identifier)
    except User.DoesNotExist:
        try:
            recipient = User.objects.get(email=recipient_identifier)
        except User.DoesNotExist:
            return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get accounts
    try:
        sender_account = UserAccount.objects.get(user=sender)
    except UserAccount.DoesNotExist:
        return Response({"detail": "Sender account not found."}, status=status.HTTP_404_NOT_FOUND)

    recipient_account, _ = UserAccount.objects.get_or_create(user=recipient)

    if sender_account.account_balance < amount:
        return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)


    # Create withdrawal record for sender
    Withdrawal.objects.create(
        user=sender,
        amount=amount,
        type="transfer",
        status=True  # Mark as successful
    )

    # Create deposit record for recipient
    Deposit.objects.create(
        user=recipient,
        amount=amount,
        type="transfer",
        coin="internal",  # You can use "internal" or "wallet"
        proof=None,
        status=True
    )

    return Response({"detail": "Transfer successful."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_deposits(request):
    user = request.user
    deposits = Deposit.objects.filter(user=user).order_by('-date')
    serializer = DepositSerializer(deposits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_withdrawals(request):
    user = request.user
    withdrawals = Withdrawal.objects.filter(user=user).order_by('-date')
    serializer = WithdrawalSerializer(withdrawals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@kyc_required
def create_withdrawal(request):
    user = request.user
    amount = request.data.get('amount')
    coin = request.data.get('coin')
    wallet = request.data.get('wallet')

    if not amount or not coin or not wallet:
        return Response({"detail": "Amount, coin, and wallet are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = int(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return Response({"detail": "Amount must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_account = UserAccount.objects.get(user=user)
    except UserAccount.DoesNotExist:
        return Response({"detail": "User account not found."}, status=status.HTTP_404_NOT_FOUND)

    if user_account.account_balance < amount:
        return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

    # # Deduct balance
    # user_account.account_balance -= amount
    # user_account.total_withdrawal += amount
    # user_account.save()

    # Create withdrawal record
    withdrawal = Withdrawal.objects.create(
        user=user,
        amount=amount,
        coin=coin,
        wallet=wallet,
        type='withdrawal',
        status=False  # Pending
    )

    send_withdrawal_mail(
                email=user.email,
                amount=amount
            )

    serializer = WithdrawalSerializer(withdrawal)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@kyc_required
def create_user_investment(request):
    user = request.user
    serializer = UserInvestmentSerializer(data=request.data)
    
    if serializer.is_valid():
        plan = serializer.validated_data['plan']
        amount = serializer.validated_data['amount']

        # Validate amount within plan limits
        if amount < plan.min_deposit or amount > plan.max_deposit:
            return Response(
                {"detail": "Amount must be between plan's min and max deposit."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has enough balance
        try:
            account = UserAccount.objects.get(user=user)
        except UserAccount.DoesNotExist:
            return Response({"detail": "User account not found."}, status=status.HTTP_404_NOT_FOUND)

        if account.account_balance < amount:
            return Response(
                {"detail": "Insufficient balance to invest."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct amount from user balance
        account.account_balance -= amount
        account.total_investment = getattr(account, 'total_investment', 0) + amount
        account.save()

        # Calculate end_date based on plan duration
        start_date = now()
        end_date = start_date + timedelta(hours=plan.duration)

        # Save investment
        UserInvestment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            type=serializer.validated_data.get('type', 'investment'),
            auto_reinvest=serializer.validated_data.get('auto_reinvest', False),
            start_date=start_date,
            end_date=end_date
        )

        return Response({"detail": "Investment created successfully."}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_active_investments(request):
    process_matured_investments() 
    user = request.user
    investments = UserInvestment.objects.filter(
        user=user,
        is_active=True,
        matured=False
    ).order_by('-start_date')

    serializer = UserListInvestmentSerializer(investments, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_kyc(request):
    user = request.user

    # Prevent resubmission
    if KYCVerification.objects.filter(user=user).exists():
        return Response({"detail": "KYC already submitted."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = KYCSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response({"detail": "KYC submitted successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_auto_reinvest(request, investment_id):
    user = request.user

    try:
        investment = UserInvestment.objects.get(id=investment_id, user=user)
    except UserInvestment.DoesNotExist:
        return Response({"detail": "Investment not found."}, status=status.HTTP_404_NOT_FOUND)

    investment.auto_reinvest = not investment.auto_reinvest
    investment.save()

    return Response({
        "detail": f"Auto reinvest set to {investment.auto_reinvest} for this investment."
    }, status=status.HTTP_200_OK)