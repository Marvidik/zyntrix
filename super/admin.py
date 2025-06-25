from django.contrib import admin
from .models import InvestmentPlan,PaymentMethods,Settings

# Register your models here.
@admin.register(InvestmentPlan)
class InvestmentPLanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'profit_percent', 'min_deposit','max_deposit')


# Register your models here.
@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    list_display = ('name', 'network', 'address')


# Register your models here.
@admin.register(Settings)
class PaymentMethodsAdmin(admin.ModelAdmin):
    list_display = ('kyc', 'verification')