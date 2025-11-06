from django.contrib import admin
from .models import Cake, Order, OrderItem, Category, Coupon, SpecialOffer, SiteSettings
from .notifications import notify_user_order_status

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'featured', 'category', 'created_at')
    list_filter = ('featured', 'category', 'created_at')
    search_fields = ('name', 'description')

@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'discount_amount', 'minimum_order_value', 'active', 'valid_from', 'valid_until')
    list_filter = ('active', 'valid_from', 'valid_until')
    search_fields = ('title', 'description')
    list_editable = ('active', 'discount_percentage', 'discount_amount', 'minimum_order_value')

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
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ('mark_confirmed', 'mark_preparing', 'mark_ready_for_pickup', 'mark_out_for_delivery', 'mark_picked_up', 'mark_cancelled')

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0
        fields = ('cake', 'quantity', 'price')
        readonly_fields = ()

    inlines = [OrderItemInline]

    def _bulk_update_status(self, request, queryset, new_status, label):
        updated = 0
        for order in queryset:
            if order.status != new_status:
                order.status = new_status
                order.save(update_fields=['status', 'updated_at'])
                try:
                    notify_user_order_status(order)
                except Exception:
                    pass
                updated += 1
        self.message_user(request, f"{updated} order(s) marked as {label}.")

    def mark_confirmed(self, request, queryset):
        self._bulk_update_status(request, queryset, 'confirmed', 'confirmed')
    mark_confirmed.short_description = 'Mark selected orders as Confirmed'

    def mark_preparing(self, request, queryset):
        self._bulk_update_status(request, queryset, 'processing', 'Preparing')
    mark_preparing.short_description = 'Mark selected orders as Preparing'

    def mark_ready_for_pickup(self, request, queryset):
        self._bulk_update_status(request, queryset, 'ready_for_pickup', 'Ready for Pickup')
    mark_ready_for_pickup.short_description = 'Mark selected orders as Ready for Pickup'

    def mark_out_for_delivery(self, request, queryset):
        self._bulk_update_status(request, queryset, 'out_for_delivery', 'Out for Delivery')
    mark_out_for_delivery.short_description = 'Mark selected orders as Out for Delivery'

    def mark_picked_up(self, request, queryset):
        self._bulk_update_status(request, queryset, 'picked_up', 'Picked Up')
    mark_picked_up.short_description = 'Mark selected orders as Picked Up'

    def mark_cancelled(self, request, queryset):
        self._bulk_update_status(request, queryset, 'cancelled', 'Cancelled')
    mark_cancelled.short_description = 'Mark selected orders as Cancelled'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'cake', 'quantity', 'price')
    list_filter = ('order__status',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone', 'created_at')
    search_fields = ('site_name', 'email')
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'logo', 'hero_image')
        }),
        ('About Section Images', {
            'fields': ('about_image_1', 'about_image_2', 'about_image_3', 'about_image_4')
        }),
        ('Social Media Links', {
            'fields': ('instagram_url', 'facebook_url', 'twitter_url', 'email')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Allow only one SiteSettings instance
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)
