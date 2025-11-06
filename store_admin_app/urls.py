from django.urls import path
from . import views

app_name = 'store_admin_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('store-settings/', views.store_settings, name='store_settings'),
]
