from django.contrib import admin

from .models import Account, Transaction, Record, Category, Product

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'currency')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'state')

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('registered', 'barcode', 'name', 'currency', 'account')
    list_filter = ('state',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'barcode')

