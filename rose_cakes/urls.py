from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('catalog/', views.catalog, name='catalog'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('add-to-cart/<int:cake_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:cake_id>/', views.buy_now, name='buy_now'),
    path('remove-from-cart/<int:cake_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('payment-success/', views.payment_success, name='payment_success'),
]
