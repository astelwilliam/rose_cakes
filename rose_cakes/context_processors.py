from .models import SiteSettings

def site_settings(request):
    """Context processor to add site settings to all templates"""
    return {'site_settings': SiteSettings.get_settings()}
