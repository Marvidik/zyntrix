from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib.auth.models import User
from super.models import InvestmentPlan
from user.models import (
    UserInvestment, Withdrawal, Deposit,
    KYCVerification, ReferalBonus,UserProfile,UserAccount, Profit
)
from user.utils import update_user_account, process_matured_investments
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views import View


@staff_member_required
def admin_dashboard(request):
    process_matured_investments()
    accounts = UserAccount.objects.select_related("user")

    user_data = []
    for acc in accounts:
        profile = UserProfile.objects.filter(user=acc.user).first()
        full_name = profile.full_name if profile else acc.user.username
        initials = ''.join([name[0] for name in full_name.split()[:2]]).upper()

        kyc_verified = KYCVerification.objects.filter(user=acc.user, is_approved=True).exists()

        user_data.append({
            'id': acc.user.id,
            'name': full_name,
            'initials': initials,
            'email': acc.user.email,
            'account_balance': acc.account_balance,
            'withdrawal': acc.total_withdrawal,
            'profit':acc. total_profit,
            'bonus': acc.bonus + acc.referal_bonus,
            'deposit': acc.total_deposit,
            'kyc': kyc_verified,
        })
    context = {
        "user_total_count": User.objects.count(),
        "user_unverified_count": UserProfile.objects.filter(status="Not Verified").count(),
        "user_verified_count": UserProfile.objects.filter(status="Verified").count(),

        "investment_total_amount": UserInvestment.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "investment_unread_count": UserInvestment.objects.filter(matured=False).count(),
        "investment_read_count": UserInvestment.objects.filter(matured=True).count(),

        "withdrawal_total_amount": Withdrawal.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "withdrawal_unread_count": Withdrawal.objects.filter(status=False).count(),
         "withdrawal_read_count": Withdrawal.objects.filter(status=True).count(),

        "deposit_total_amount": Deposit.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "deposit_unread_count": Deposit.objects.filter(status=False).count(),
        "deposit_read_count": Deposit.objects.filter(status=True).count(),

        "kyc_total_count": KYCVerification.objects.count(),
        "kyc_unread_count": KYCVerification.objects.filter(is_approved=False).count(),
        "kyc_read_count": KYCVerification.objects.filter(is_approved=True).count(),

        "referal_total_amount": ReferalBonus.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "referal_unread_count": ReferalBonus.objects.count(),  

         'users': user_data,
    }

    return render(request, "dashboard/dash.html", context)





def update_all_user_accounts():

    process_matured_investments()
    User = get_user_model()
    for user in User.objects.all():
        update_user_account(user)


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class UpdateAccountsAjaxView(View):
    def get(self, request):
        update_all_user_accounts()
        return JsonResponse({"message": "All user accounts updated!"})