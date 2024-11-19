from django.contrib import admin
from .models import CommissionSetting, PaybookEntry,PayoutRequest

@admin.register(CommissionSetting)
class CommissionSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'commission_type', 'commission_value', 'updated_at')
    list_filter = ('commission_type',)
    search_fields = ('commission_type',)
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Restrict to allow only one CommissionSetting to ensure single configuration
        if CommissionSetting.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Restrict deletion to maintain single configuration setup
        return False

@admin.register(PaybookEntry)
class PaybookEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'mentor', 'amount_paid', 'commission_deducted', 'credited_to_wallet', 'created_at')
    list_filter = ('mentor', 'created_at')
    search_fields = ('mentor__username', 'booking__id')
    readonly_fields = ('booking', 'mentor', 'amount_paid', 'commission_deducted', 'credited_to_wallet', 'created_at')

    def has_add_permission(self, request):
        # Prevent direct addition of Paybook entries through the admin (only via transactions)
        return False
@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'mentor', 'amount', 'status', 'requested_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('mentor__name',)
