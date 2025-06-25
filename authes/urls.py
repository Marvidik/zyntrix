from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('register',register_user,name="register" ),
    path('login',login_user,name="login"),
    path('verify/<int:user_id>', verify_account, name='verify-account'),
    path('otp',request_otp,name="otp"),
    path('verify-otp',verify_otp,name="verify-otp"),
    path('change-password',change_password,name="change-password"),
    path('reset-password',reset_password_by_email,name="reset-password"),
   
]
