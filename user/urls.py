from django.urls import path,include
from .views import  *
urlpatterns = [
    path("dashboard",get_account_info,name="dashboard"),
    path('history',transaction_history,name="history"),
    path('deposit',create_deposit,name="deposit"),
    path('profits',get_user_profits,name="profits"),
    path('referals',get_referal_list,name="referal-list"),
    path('profile/update',update_profile,name="update-profile"),
    path('profile/withdrawal/create',create_or_update_withdrawal_info,name="create-withdrawal"),
    path('profile/withdrawal/list',get_withdrawal_info,name="list-withdrawal"),
    path('settings/notifications', create_or_update_other_settings, name='create_or_update_other_settings'),
    path('other-settings', get_user_other_settings, name='user-other-settings'),
    path('transfer', transfer_funds, name='transfer_funds'),
    path('deposits/', get_user_deposits, name='get_user_deposits'),
    path('withdrawals/', get_user_withdrawals, name='get_user_withdrawals'),
    path('withdraw', create_withdrawal, name='create_withdrawal'),
    path('investments/create', create_user_investment, name='create-user-investment'),
    path('investments/active', list_active_investments, name='list-active-investments'),
    path('kyc/submit', submit_kyc, name='submit-kyc'),
    path('investment/<int:investment_id>/toggle-auto-reinvest', toggle_auto_reinvest, name='toggle-auto-reinvest'),
]
