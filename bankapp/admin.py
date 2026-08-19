from django.contrib import admin
from bankapp.models import reg, Transaction

@admin.register(reg)
class RegAdmin(admin.ModelAdmin):
    list_display = ('accno', 'name', 'amount', 'mobileno', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('accno', 'name', 'mobileno')
    readonly_fields = ('created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('account__accno', 'account__name', 'description')
    readonly_fields = ('created_at',)