from django.contrib import admin
from .models import Product, Shelter, Donation


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'address', 'phone')
    list_filter = ('region',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'shelter', 'product', 'amount', 'created_at')
    list_filter = ('shelter',)