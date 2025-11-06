from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rose_cakes.models import SiteSettings

@login_required
def dashboard(request):
    return render(request, 'store_admin_app/dashboard.html')

@login_required
def store_settings(request):
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        settings_obj.store_name = request.POST.get('store_name', settings_obj.store_name)
        settings_obj.store_address = request.POST.get('store_address', settings_obj.store_address)
        settings_obj.store_phone = request.POST.get('store_phone', settings_obj.store_phone)
        settings_obj.store_email = request.POST.get('store_email', settings_obj.store_email)
        settings_obj.store_description = request.POST.get('store_description', settings_obj.store_description)
        settings_obj.facebook_url = request.POST.get('facebook_url', settings_obj.facebook_url)
        settings_obj.instagram_url = request.POST.get('instagram_url', settings_obj.instagram_url)
        settings_obj.whatsapp_number = request.POST.get('whatsapp_number', settings_obj.whatsapp_number)
        settings_obj.save()
        messages.success(request, 'Store settings updated successfully!')
        return redirect('store_admin_app:store_settings')
    return render(request, 'store_admin_app/store_settings.html', {'settings': settings_obj})
