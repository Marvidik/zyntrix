from rest_framework import serializers
from .models import WithdrawalInfo,OtherSettings,Deposit,Withdrawal,UserInvestment,KYCVerification

class WithdrawalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalInfo
        fields = '__all__'
        read_only_fields = ['user']


class OtherSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherSettings
        fields = '__all__'
        read_only_fields = ['user']

class OtherSettingsSerializerr(serializers.ModelSerializer):
    class Meta:
        model = OtherSettings
        fields = ['send_otp_on_withdrawal', 'notify_on_profit', 'notify_on_plan_expiry']


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = '__all__'
        read_only_fields = ['user', 'type', 'status', 'date']


class UserInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvestment
        fields = ['plan', 'amount', 'type', 'auto_reinvest'] 


class UserListInvestmentSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    class Meta:
        model = UserInvestment
        fields = [
            'id', 'plan_name', 'amount', 'type', 'start_date',
            'end_date', 'profit_earned', 'is_active',
            'matured', 'auto_reinvest'
        ]



# serializers.py


class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        exclude = ['is_approved', 'submitted_at', 'user']
        extra_kwargs = {
            'email': {'required': True},
            'all_info_confirmed': {'required': True}
        }

    def validate(self, data):
        if not data.get('all_info_confirmed'):
            raise serializers.ValidationError("You must confirm that all information entered is correct.")
        return data
