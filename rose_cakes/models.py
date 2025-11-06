from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cake(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cakes/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Weight in kg")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SpecialOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount percentage (e.g., 10 for 10%)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Fixed discount amount (alternative to percentage)")
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order value to apply offer")
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_until

    def get_discount_amount(self, order_total):
        if not self.is_valid() or order_total < self.minimum_order_value:
            return 0
        
        if self.discount_percentage > 0:
            return order_total * (self.discount_percentage / 100)
        elif self.discount_amount > 0:
            return min(self.discount_amount, order_total)
        return 0

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Preparing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    pickup_date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    special_offer = models.ForeignKey(SpecialOffer, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.cake.name}"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Rose Cakes")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Upload site logo")
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Main hero image for homepage")
    about_image_1 = models.ImageField(upload_to='site/', blank=True, null=True, help_text="About section image 1")
    about_image_2 = models.ImageField(upload_to='site/', blank=True, null=True, help_text="About section image 2")
    about_image_3 = models.ImageField(upload_to='site/', blank=True, null=True, help_text="About section image 3")
    about_image_4 = models.ImageField(upload_to='site/', blank=True, null=True, help_text="About section image 4")
    
    # Social Media Links
    instagram_url = models.URLField(blank=True, null=True, help_text="Instagram profile URL")
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook page URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter profile URL")
    email = models.EmailField(blank=True, null=True, help_text="Contact email address")
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Store Description
    store_description = models.TextField(blank=True, null=True, help_text="Store description")

    # WhatsApp
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, help_text="WhatsApp number")

    # SEO and Meta
    meta_description = models.TextField(blank=True, null=True, help_text="Site meta description for SEO")
    meta_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated keywords")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        """Get the first (and typically only) site settings instance"""
        return cls.objects.first()
