from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from super.models import InvestmentPlan
# Create your models here.


class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    full_name= models.CharField(max_length=100)
    phone= models.CharField(max_length=18)
    country= models.CharField(max_length=100)
    account_type= models.CharField(max_length=100)
    dob= models.DateTimeField(null=True, blank=True)
    address= models.CharField(max_length=100,null=True, blank=True)
    status=models.CharField(default="Not Verified")
    kyc=models.BooleanField(default=False)

class WithdrawalInfo(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    # Bank Information
    bank_name = models.CharField(max_length=100,null=True, blank=True)
    account_name = models.CharField(max_length=100,null=True, blank=True)
    account_number = models.CharField(max_length=20,null=True, blank=True)
    swift_code = models.CharField(max_length=20,null=True, blank=True)

    # Cryptocurrency Information
    bitcoin_address = models.CharField(max_length=200,null=True, blank=True)
    ethereum_address = models.CharField(max_length=200,null=True, blank=True)
    litecoin_address = models.CharField(max_length=200,null=True, blank=True)
    usdt_trc20_address = models.CharField(max_length=200,null=True, blank=True)

    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"
    

class OtherSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    send_otp_on_withdrawal = models.BooleanField(default=True)
    notify_on_profit = models.BooleanField(default=True)
    notify_on_plan_expiry = models.BooleanField(default=True)

    def __str__(self):
        return f"Email Settings for {self.user.username}"
    
class KYCVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    social_username = models.CharField(max_length=100)  # Twitter or Facebook

    # Address Details
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    # Document Upload
    document_front = models.FileField(upload_to='kyc-documents/front/')
    document_back = models.FileField(upload_to='kyc-documents/back/')

    all_info_confirmed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update related user profile
        try:
            profile, _ = UserProfile.objects.get_or_create(user=self.user)
            profile.kyc = self.is_approved
            profile.save()
        except Exception as e:
            print(f"Error updating UserProfile KYC flag: {e}")
            
    def __str__(self):
        return f"KYC for {self.user.username}"

class Otp(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.IntegerField()


class Deposit(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.IntegerField()
    type=models.CharField(max_length=50,default="deposit")
    coin=models.CharField(max_length=50)
    proof=models.FileField(upload_to="deposit-prove")
    date=models.DateTimeField(default=now)
    status=models.BooleanField(default=False)

class Bonus(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.IntegerField()
    type=models.CharField(max_length=50,default="bonus")
    date=models.DateTimeField(default=now)

class Penalty(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.IntegerField()
    type=models.CharField(max_length=50,default="bonus")
    reason=models.CharField(max_length=100)
    date=models.DateTimeField(default=now)


class ReferalBonus(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.IntegerField()
    type=models.CharField(max_length=50,default="ref-bonus")
    date=models.DateTimeField(default=now)


class Withdrawal(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    amount= models.IntegerField()
    type= type=models.CharField(max_length=50, default="withdrawal")
    date=models.DateTimeField(default=now)
    status=models.BooleanField(default=False)
    coin=models.CharField(max_length=50,default='btc')
    wallet=models.CharField(max_length=50,default='none')


class Profit(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    plan= models.CharField(max_length=100, default="Basic")
    amount= models.IntegerField()
    type=models.CharField(max_length=50, default="profit")
    date=models.DateTimeField(default=now)


class ReferalList(models.Model):
    client_name=models.CharField(max_length=100)
    ref_level=models.IntegerField(default=0)
    client_status=models.CharField(max_length=50)
    date_registered=models.DateTimeField(default=now)



class UserInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    type = models.CharField(max_length=50, default="investment")

    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(blank=True, null=True)
    
    profit_earned = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    matured = models.BooleanField(default=False)
    auto_reinvest=models.BooleanField(default=False)

    

class UserAccount(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    account_balance= models.IntegerField(default=0)
    total_profit=models.IntegerField(default=0)
    bonus=models.IntegerField(default=0)
    referal_bonus=models.IntegerField(default=0)
    total_deposit=models.IntegerField(default=0)
    total_withdrawal=models.IntegerField(default=0)


