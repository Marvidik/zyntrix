from rest_framework import serializers
from django.contrib.auth.models import User
from user.models import *
from  super.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]  


# For listing users
class UserProfileListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ["id", "full_name", "phone", "country", "account_type", "status", "kyc", "user"]


#  For detailed view (include everything)
class UserProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"


class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = "__all__"
        read_only_fields = ["id", "submitted_at", "user"]


class DepositSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = Deposit
        fields = "__all__"
        read_only_fields = ["id", "user", "date", "type", "proof"]


class WithdrawalSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = Withdrawal
        fields = "__all__"
        read_only_fields = ["id", "user", "date", "type"]


class ProfitSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profit
        fields = "__all__"

class ReferalListSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ReferalList
        fields = "__all__"

class BonusSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Bonus
        fields = "__all__"

class PenaltySerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Penalty
        fields = "__all__"

class ReferalBonusSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ReferalBonus
        fields = "__all__"


class InvestmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlan
        fields = "__all__"