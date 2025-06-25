from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Deposit, Bonus, ReferalBonus, Withdrawal, UserInvestment, UserAccount, ReferalList,Profit,Penalty,KYCVerification

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Unregister the original User admin, then register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)




@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'coin', 'date', 'status')
    list_filter = ('status', 'coin', 'date')
    search_fields = ('user__username', 'coin')
    date_hierarchy = 'date'

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'date')
    list_filter = ('type', 'date')
    search_fields = ('user__username',)

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'date')
    list_filter = ('type', 'date')
    search_fields = ('user__username',)

@admin.register(ReferalBonus)
class ReferalBonusAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'date')
    list_filter = ('type', 'date')
    search_fields = ('user__username',)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type' ,'status', 'date')
    list_filter = ('type',)
    search_fields = ('user__username',)

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'account_balance', 'total_profit',
        'bonus', 'referal_bonus', 'total_deposit', 'total_withdrawal'
    )
    search_fields = ('user__username',)
    list_filter = ('account_balance',)

@admin.register(ReferalList)
class ReferalListAdmin(admin.ModelAdmin):
    list_display=(
        'client_name', 'ref_level', "client_status", "date_registered"
    )

@admin.register(UserInvestment)
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'type', 'start_date', 'end_date', 'profit_earned', 'is_active', 'matured')


@admin.register(Profit)
class ProfitAdmin(admin.ModelAdmin):
    list_display=(
        'user', 'plan', 'amount','type', 'date'
    )



@admin.register(KYCVerification)
class KYCAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'date_of_birth',
        'nationality',
        'is_approved',
        'submitted_at'
    )
    search_fields = ('user__username', 'first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('is_approved', 'nationality', 'submitted_at')
    readonly_fields = ('submitted_at',)