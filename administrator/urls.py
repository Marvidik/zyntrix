from django.urls import path,include
from .views import  *
urlpatterns = [
    path('users', user_list, name='user-list'),
    path('users/<int:pk>', user_detail, name='user-detail'),

    path("dashboard", dashboard_data, name="dashboard-data"),

    path("kyc/", list_kyc_applications, name="list-kyc"),
    path("kyc/<int:pk>", approve_kyc, name="approve-kyc"),

    path("deposits", list_deposits, name="list-deposits"),
    path("deposits/<int:pk>/approve", approve_deposit, name="approve-deposit"),

    path("withdrawals", list_withdrawals, name="list-withdrawals"),
    path("withdrawals/<int:pk>/approve", approve_withdrawal, name="approve-withdrawal"),

    path("profits", list_profits, name="list_profits"),
    path("referrals", list_referrals, name="list_referrals"),
    path("bonuses", list_bonuses, name="list_bonuses"),
    path("penalties", list_penalties, name="list_penalties"),
    path("referral-bonuses", list_referral_bonuses, name="list_referral_bonuses"),

    path("bonuses/create", create_bonus, name="create_bonus"),
    path("penalties/create", create_penalty, name="create_penalty"),

    path('active-investments', list_investments, name='list-active-investments'),

    path("plans", investment_plan_list_create, name="plan-list-create"),
    path("plans/<int:pk>", investment_plan_detail, name="plan-detail"),

    path("payment-methods", list_payment_methods, name="list_payment_methods"),
    path("payment-methods/create", create_payment_method, name="create_payment_method"),
    path("payment-methods/<int:pk>/update", update_payment_method, name="update_payment_method"),
    path("payment-methods/<int:pk>/delete",delete_payment_method, name="delete_payment_method"),

    path("settings", settings_view, name="settings"),
]

