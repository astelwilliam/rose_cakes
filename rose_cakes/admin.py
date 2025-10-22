from django.contrib import admin
from .models import Cake, Order, OrderItem, Category, Coupon

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'featured', 'category', 'created_at')
    list_filter = ('featured', 'category', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active', 'valid_from', 'valid_until', 'used_count')
    list_filter = ('active', 'valid_from', 'valid_until')
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'total_amount', 'status', 'user', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('customer_name', 'customer_email', 'tracking_number')
    readonly_fields = ('payment_id', 'tracking_number', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'cake', 'quantity', 'price')
    list_filter = ('order__status',)
