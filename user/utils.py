from django.db.models import Sum
from .models import UserAccount, Deposit, Bonus, ReferalBonus, Withdrawal,Profit,Penalty,UserInvestment
from django.core.mail import send_mail
from django.utils.html import format_html
import os
from django.utils.timezone import now,timedelta


def update_user_account(user):
    # Aggregate deposit (only confirmed)
    total_deposit = Deposit.objects.filter(user=user, status=True).aggregate(total=Sum('amount'))['total'] or 0

    # Aggregate withdrawal
    total_withdrawal = Withdrawal.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

    # Aggregate bonuses
    bonus = Bonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    penalty = Penalty.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    referal_bonus = ReferalBonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

    total_profit = Profit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    # Calculate profit and balance
    investment=UserInvestment.objects.filter(user=user,is_active=True,matured=False).aggregate(total=Sum('amount'))['total'] or 0

    account_balance = total_deposit + total_profit + bonus + referal_bonus - total_withdrawal - penalty - investment

    # Update the UserAccount
    account, created = UserAccount.objects.get_or_create(user=user)
    account.account_balance = account_balance
    account.total_profit = total_profit
    account.bonus = bonus
    account.referal_bonus = referal_bonus
    account.total_deposit = total_deposit
    account.total_withdrawal = total_withdrawal
    account.save()


def process_matured_investments():
    matured_count = 0
    reinvested_count = 0

    investments = UserInvestment.objects.filter(is_active=True, end_date__lte=now())

    for investment in investments:
        profit_amount = int((investment.amount * investment.plan.profit_percent) / 100)

        # Mark as matured
        investment.matured = True
        investment.is_active = False
        investment.profit_earned = profit_amount
        investment.save()

        # Create profit record
        Profit.objects.create(
            user=investment.user,
            plan=investment.plan.name,
            amount=profit_amount,
            type="profit"
        )
        matured_count += 1

        # Auto reinvest if enabled
        if investment.auto_reinvest:
            new_start = investment.end_date
            new_end = new_start + timedelta(hours=investment.plan.duration)

            UserInvestment.objects.create(
                user=investment.user,
                plan=investment.plan,
                amount=investment.amount,
                type="investment",
                auto_reinvest=True,
                start_date=new_start,
                end_date=new_end
            )

            reinvested_count += 1

    return {"matured": matured_count, "reinvested": reinvested_count}


def send_deposit_mail(email,amount):
    try:
        subject = "Deposit Request"
        message = format_html("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    background-color: #f0f4f8;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: #0051a2;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    color: #333;
                }}
                .content h2 {{
                    color: #0051a2;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    background-color: #f0f4f8;
                    text-align: center;
                    padding: 15px;
                    font-size: 14px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Deposit Request</h1>
                </div>
                <div class="content">
                    <h2>Hello ,</h2>
                    <p>You submitted a <strong>Deposit</strong> — request for your account.</p>
                    <p>Amount:${amount}</p>
                    <p>Your request has been received and will be processed shortly</p>         

                    <p style="margin-top: 20px;">Please keep your login credentials safe. Our platform will never ask for your password, OTP, or personal codes.</p>
                    <p>– The Parkland Team</p>
                </div>
                <div class="footer">
                    &copy; 2025 Parkland Oil and Gas. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """, amount=amount)

        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        recipient_list = [email]

        send_mail(subject, '', from_email, recipient_list, html_message=message, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False


def send_withdrawal_mail(email,amount):
    try:
        subject = "Withdrawal Request"
        message = format_html("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    background-color: #f0f4f8;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: #0051a2;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    color: #333;
                }}
                .content h2 {{
                    color: #0051a2;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                .footer {{
                    background-color: #f0f4f8;
                    text-align: center;
                    padding: 15px;
                    font-size: 14px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Withdrawal Request</h1>
                </div>
                <div class="content">
                    <h2>Hello ,</h2>
                    <p>You submitted a <strong>Withdrawal</strong> — request for your account.</p>
                    <p>Amount: ${amount}</p>
                    <p>Your request has been received and will be processed shortly</p>         

                    <p style="margin-top: 20px;">Please keep your login credentials safe. Our platform will never ask for your password, OTP, or personal codes.</p>
                    <p>– The Parkland Team</p>
                </div>
                <div class="footer">
                    &copy; 2025 Parkland Oil and Gas. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """, amount=amount)

        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        recipient_list = [email]

        send_mail(subject, '', from_email, recipient_list, html_message=message, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False
