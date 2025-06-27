from django.core.mail import send_mail
from django.utils.html import format_html
import os
import random
import string
from django.contrib.auth.models import User
from user.models import ReferalBonus,ReferalList, UserProfile
from user.utils import update_user_account


def generate_numeric_otp(length=4):
    """Generate a random numeric OTP of given length (default: 6 digits)."""
    return ''.join(random.choices(string.digits, k=length))



def send_welcome_mail(email, full_name, username,account_type,user_id):
    try:
        subject = "Welcome to Parkland Oil and Gas"
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
                    <h1>Welcome to Parkland Oil and Gas</h1>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <p>Thank you for joining <strong>Parkland</strong> — your new home for smart, secure, and rewarding investments.</p>
                    <p>Here’s a quick summary of your profile:</p>
                    <table>
                        <tr>
                            <td><strong>Username:</strong></td>
                            <td>{username}</td>
                        </tr>
                        <tr>
                            <td><strong>Account Type:</strong></td>
                            <td>{account_type}</td>
                        </tr>
                        <p>Verify Your Account with the Link Below</p>
                        <p>https://www.parklandoilassetslimited.com/auth/verify-account?user={user_id}</p>
                    </table>
                    <p style="margin-top: 20px;">Please keep your login credentials safe. Our platform will never ask for your password, OTP, or personal codes.</p>
                    <p>We're excited to have you on board.</p>
                    <p>– The Parkland Team</p>
                </div>
                <div class="footer">
                    &copy; 2025 Parkland Oil and Gas. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """, full_name=full_name, username=username, account_type=account_type,user_id=user_id)

        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        recipient_list = [email]

        send_mail(subject, '', from_email, recipient_list, html_message=message, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False
    


def send_otp_mail(email, otp):
    try:
        subject = "OTP Request"
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
                    <h1>OTP Request</h1>
                </div>
                <div class="content">
                    <h2>Hello ,</h2>
                    <p>You requested for <strong>OTP</strong> —  for your account.</p>
                    <p>Your Otp Is:</p>
                    
                    <h2>OTP: {otp}</h2>

                    <p style="margin-top: 20px;">Please keep your login credentials safe. Our platform will never ask for your password, OTP, or personal codes.</p>
                    <p>We're excited to have you on board.</p>
                    <p>– The Parkland Team</p>
                </div>
                <div class="footer">
                    &copy; 2025 Parkland Oil and Gas. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """, otp=otp)

        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        recipient_list = [email]

        send_mail(subject, '', from_email, recipient_list, html_message=message, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False



def process_referral(referee_username, new_user, bonus_amount=5):
    """
    Process referral bonus and create referral records
    
    Args:
        referee_username: Username of the referring user
        new_user: The newly registered user object
        bonus_amount: Bonus amount to award (default: 100)
    
    Returns:
        bool: True if referral was processed successfully, False otherwise
    """
    if not referee_username:
        return False
        
    try:
        referee = User.objects.get(username=referee_username)
        
        # Create referral bonus for the referee
        ReferalBonus.objects.create(
            user=referee,
            amount=bonus_amount
        )
        
       

        

        # Create referral list entry
        ReferalList.objects.create(
            client_name=new_user.username,
            ref_level=1,
            client_status="registered"
        )
        
        user= User.objects.filter(username=referee_username).first()

        update_user_account(user)

        return True
        
    except User.DoesNotExist:
        # Log this if needed: referee doesn't exist
        return False
    except Exception as e:
        # Log the error if needed
        return False