from django.db.models import Sum
from django.db.models import Sum
from user.models import UserAccount, Deposit, Bonus, ReferalBonus, Withdrawal,Profit,Penalty,UserInvestment
from django.core.mail import send_mail
from django.utils.html import format_html
import os
from django.utils.timezone import now,timedelta


def update_user_account(user):
    """
    Updates or creates a UserAccount for the given user.
    """

    total_deposit = Deposit.objects.filter(user=user, status=True).aggregate(total=Sum('amount'))['total'] or 0
    total_withdrawal = Withdrawal.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    bonus = Bonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    penalty = Penalty.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    referal_bonus = ReferalBonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_profit = Profit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    active_investment = UserInvestment.objects.filter(user=user, is_active=True, matured=False).aggregate(total=Sum('amount'))['total'] or 0

    account_balance = (
        total_deposit
        + total_profit
        + bonus
        + referal_bonus
        - total_withdrawal
        - penalty
        - active_investment
    )

    account, created = UserAccount.objects.get_or_create(user=user)
    account.account_balance = account_balance
    account.total_profit = total_profit
    account.bonus = bonus
    account.referal_bonus = referal_bonus
    account.total_deposit = total_deposit
    account.total_withdrawal = total_withdrawal
    account.save()

    return account   # ✅ ALWAYS return the account

