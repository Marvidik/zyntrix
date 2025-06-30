from django.urls import path
from .views import admin_dashboard,UpdateAccountsAjaxView

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('update-users/', UpdateAccountsAjaxView.as_view(), name='run-account-update'),
]
