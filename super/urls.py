# urls.py

from django.urls import path
from .views import list_investment_plans,list_payment_methods

urlpatterns = [
    path('plans', list_investment_plans, name='list-plans'),
    path('payment-methods', list_payment_methods, name='list-payment-methods'),
]
