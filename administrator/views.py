from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from  user.models import UserProfile
from .serializers import UserProfileListSerializer, UserProfileDetailSerializer,KYCVerificationSerializer,DepositSerializer,WithdrawalSerializer,ProfitSerializer,ReferalListSerializer,BonusSerializer,PenaltySerializer,ReferalBonusSerializer,InvestmentPlanSerializer
from django.db.models import Sum
from django.contrib.auth.models import User
from user.models import (
    UserInvestment, Withdrawal, Deposit, KYCVerification,
    ReferalBonus, UserProfile, UserAccount, Profit,Bonus, Penalty, ReferalList
)
from user.utils import process_matured_investments
from .utils import update_user_account
from  super.models import *

# List users with limited info
@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_list(request):
    users = UserProfile.objects.all()
    serializer = UserProfileListSerializer(users, many=True)
    return Response(
        {
            "status": "success",
            "message": "Users retrieved successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


# User details with full info
@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_detail(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)
    serializer = UserProfileDetailSerializer(user_profile)
    return Response(
        {
            "status": "success",
            "message": f"User {pk} retrieved successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )



@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_data(request):
    # update matured investments first
    process_matured_investments()

    user_data = []

    for user in User.objects.all():
        # Run update before collecting stats
        account = update_user_account(user)


        profile = UserProfile.objects.filter(user=user).first()
        full_name = profile.full_name if profile else user.username
        initials = ''.join([name[0] for name in full_name.split()[:2]]).upper()

        kyc_verified = KYCVerification.objects.filter(user=user, is_approved=True).exists()

        user_data.append({
            "id": user.id,
            "name": full_name,
            "initials": initials,
            "email": user.email,
            "account_balance": account.account_balance,
            "withdrawal": account.total_withdrawal,
            "profit": account.total_profit,
            "bonus": account.bonus + account.referal_bonus,
            "deposit": account.total_deposit,
            "kyc": kyc_verified,
        })

    data = {
        "status": "success",
        "message": "Dashboard data retrieved successfully",
        "data": {
            "users": {
                "total": User.objects.count(),
                "verified": UserProfile.objects.filter(status="Verified").count(),
                "unverified": UserProfile.objects.filter(status="Not Verified").count(),
            },
            "investment": {
                "total_amount": UserInvestment.objects.aggregate(total=Sum("amount"))["total"] or 0,
                "completed": UserInvestment.objects.filter(matured=True).count(),
                "active": UserInvestment.objects.filter(matured=False).count(),
            },
            "withdrawal": {
                "total_amount": Withdrawal.objects.aggregate(total=Sum("amount"))["total"] or 0,
                "completed": Withdrawal.objects.filter(status=True).count(),
                "pending": Withdrawal.objects.filter(status=False).count(),
            },
            "deposit": {
                "total_amount": Deposit.objects.aggregate(total=Sum("amount"))["total"] or 0,
                "approved": Deposit.objects.filter(status=True).count(),
                "pending": Deposit.objects.filter(status=False).count(),
            },
            "kyc": {
                "total": KYCVerification.objects.count(),
                "approved": KYCVerification.objects.filter(is_approved=True).count(),
                "pending": KYCVerification.objects.filter(is_approved=False).count(),
            },
            "referrals": {
                "total_amount": ReferalBonus.objects.aggregate(total=Sum("amount"))["total"] or 0,
                "count": ReferalBonus.objects.count(),
            },
            "user_data": user_data, 
        }
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_kyc_applications(request):
    kycs = KYCVerification.objects.all().order_by("-submitted_at")
    serializer = KYCVerificationSerializer(kycs, many=True)
    return Response({
        "status": "success",
        "message": "KYC applications retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def approve_kyc(request, pk):
    try:
        kyc = KYCVerification.objects.get(pk=pk)
    except KYCVerification.DoesNotExist:
        return Response({"error": "KYC application not found"}, status=status.HTTP_404_NOT_FOUND)

    # Only allow updating `is_approved` or `all_info_confirmed`
    data = {}
    if "is_approved" in request.data:
        data["is_approved"] = request.data["is_approved"]
    if "all_info_confirmed" in request.data:
        data["all_info_confirmed"] = request.data["all_info_confirmed"]

    serializer = KYCVerificationSerializer(kyc, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "KYC application updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_deposits(request):
    deposits = Deposit.objects.all().order_by("-date")
    serializer = DepositSerializer(deposits, many=True)
    return Response({
        "status": "success",
        "message": "All deposits retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def approve_deposit(request, pk):
    try:
        deposit = Deposit.objects.get(pk=pk)
    except Deposit.DoesNotExist:
        return Response({"error": "Deposit not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepositSerializer(deposit, data={"status": True}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Deposit approved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_withdrawals(request):
    withdrawals = Withdrawal.objects.all().order_by("-date")
    serializer = WithdrawalSerializer(withdrawals, many=True)
    return Response({
        "status": "success",
        "message": "All withdrawals retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def approve_withdrawal(request, pk):
    try:
        withdrawal = Withdrawal.objects.get(pk=pk)
    except Withdrawal.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Withdrawal not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = WithdrawalSerializer(withdrawal, data={"status": True}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Withdrawal approved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_profits(request):
    profits = Profit.objects.all()
    serializer = ProfitSerializer(profits, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_referrals(request):
    referrals = ReferalList.objects.all()
    serializer = ReferalListSerializer(referrals, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_bonuses(request):
    bonuses = Bonus.objects.all()
    serializer = BonusSerializer(bonuses, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_penalties(request):
    penalties = Penalty.objects.all()
    serializer = PenaltySerializer(penalties, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_referral_bonuses(request):
    referral_bonuses = ReferalBonus.objects.all()
    serializer = ReferalBonusSerializer(referral_bonuses, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_bonus(request):
    try:
        user_id = request.data.get("user_id")
        amount = request.data.get("amount")

        if not user_id or not amount:
            return Response({"error": "user_id and amount are required"}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        bonus = Bonus.objects.create(user=user, amount=amount)
        return Response({
            "status": "success",
            "message": "Bonus created successfully",
            "data": {
                "id": bonus.id,
                "user_id": user.id,
                "user_email": user.email,
                "amount": bonus.amount,
                "type": bonus.type,
                "date": bonus.date
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_penalty(request):
    try:
        user_id = request.data.get("user_id")
        amount = request.data.get("amount")
        reason = request.data.get("reason")

        if not user_id or not amount or not reason:
            return Response({"error": "user_id, amount and reason are required"}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        penalty = Penalty.objects.create(user=user, amount=amount, reason=reason)
        return Response({
            "status": "success",
            "message": "Penalty created successfully",
            "data": {
                "id": penalty.id,
                "user_id": user.id,
                "user_email": user.email,
                "amount": penalty.amount,
                "reason": penalty.reason,
                "type": penalty.type,
                "date": penalty.date
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    



@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_investments(request):
    """
    Admin-only: return all user investments in the standard response format.
    """
    investments = UserInvestment.objects.select_related("user", "plan").all()

    data = []
    for inv in investments:
        data.append({
            "id": inv.id,
            "user_id": inv.user.id,
            "user_email": inv.user.email,
            "plan": getattr(inv.plan, "name", None),
            "amount": inv.amount,
            "profit_earned": inv.profit_earned,
            "is_active": inv.is_active,
            "matured": inv.matured,
            "auto_reinvest": inv.auto_reinvest,
            "start_date": inv.start_date,
            "end_date": inv.end_date,
        })

    return Response({
        "status": "success",
        "message": "Investments retrieved successfully",
        "data": data
    }, status=status.HTTP_200_OK)



@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def investment_plan_list_create(request):
    if request.method == "GET":
        plans = InvestmentPlan.objects.all()
        serializer = InvestmentPlanSerializer(plans, many=True)
        return Response({
            "status": "success",
            "message": "Investment plans retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = InvestmentPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Investment plan created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAdminUser])
def investment_plan_detail(request, pk):
    try:
        plan = InvestmentPlan.objects.get(pk=pk)
    except InvestmentPlan.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Investment plan not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = InvestmentPlanSerializer(plan)
        return Response({
            "status": "success",
            "message": "Investment plan retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == "PATCH":
        serializer = InvestmentPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Investment plan updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        plan.delete()
        return Response({
            "status": "success",
            "message": "Investment plan deleted successfully",
            "data": None
        }, status=status.HTTP_200_OK)
    

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_payment_methods(request):
    methods = PaymentMethods.objects.all()
    data = [
        {
            "id": method.id,
            "name": method.name,
            "network": method.network,
            "address": method.address,
        }
        for method in methods
    ]
    return Response({
        "status": "success",
        "message": "Payment methods retrieved successfully",
        "data": data
    }, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_payment_method(request):
    try:
        name = request.data.get("name")
        network = request.data.get("network")
        address = request.data.get("address")

        if not name or not network or not address:
            return Response({
                "status": "error",
                "message": "name, network, and address are required",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        method = PaymentMethods.objects.create(
            name=name, network=network, address=address
        )
        return Response({
            "status": "success",
            "message": "Payment method created successfully",
            "data": {
                "id": method.id,
                "name": method.name,
                "network": method.network,
                "address": method.address,
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_payment_method(request, pk):
    try:
        method = PaymentMethods.objects.get(pk=pk)
    except PaymentMethods.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Payment method not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    method.name = request.data.get("name", method.name)
    method.network = request.data.get("network", method.network)
    method.address = request.data.get("address", method.address)
    method.save()

    return Response({
        "status": "success",
        "message": "Payment method updated successfully",
        "data": {
            "id": method.id,
            "name": method.name,
            "network": method.network,
            "address": method.address,
        }
    }, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_payment_method(request, pk):
    try:
        method = PaymentMethods.objects.get(pk=pk)
    except PaymentMethods.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Payment method not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    method.delete()
    return Response({
        "status": "success",
        "message": "Payment method deleted successfully",
        "data": None
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PATCH"])
@permission_classes([IsAdminUser])
def settings_view(request):
    try:
        settings = Settings.objects.first()
        if not settings:
            settings = Settings.objects.create()  # auto-create if missing
    except:
        settings = Settings.objects.create()

    if request.method == "GET":
        return Response({
            "id": settings.id,
            "kyc": settings.kyc,
            "verification": settings.verification,
        })

    if request.method == "PATCH":
        kyc = request.data.get("kyc")
        verification = request.data.get("verification")

        if kyc is not None:
            settings.kyc = kyc
        if verification is not None:
            settings.verification = verification

        settings.save()
        return Response({
            "message": "Settings updated successfully",
            "settings": {
                "id": settings.id,
                "kyc": settings.kyc,
                "verification": settings.verification,
            }
        }, status=status.HTTP_200_OK)