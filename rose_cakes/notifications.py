from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import SiteSettings, Order
import json
import urllib.request


def _send_email(recipient_email: str, subject: str, message: str) -> None:
    if not recipient_email:
        return
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', 'webmaster@localhost'))
    try:
        send_mail(subject, message, from_email, [recipient_email], fail_silently=True)
    except Exception:
        pass


def _send_whatsapp(phone_e164: str, message: str) -> None:
    # Uses WhatsApp Cloud API if settings.WHATSAPP_TOKEN and settings.WHATSAPP_PHONE_ID are configured
    token = getattr(settings, 'WHATSAPP_TOKEN', None)
    phone_id = getattr(settings, 'WHATSAPP_PHONE_ID', None)
    if not token or not phone_id or not phone_e164:
        return
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_e164,
        "type": "text",
        "text": {"body": message},
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        # Silently ignore failures to avoid blocking app flow
        pass


def _format_admin_new_order_message(order: Order) -> str:
    lines = [
        f"New order #{order.id}",
        f"Customer: {order.customer_name}",
        f"Email: {order.customer_email}",
        f"WhatsApp: {order.whatsapp_number or '-'}",
        f"Pickup date: {order.pickup_date}",
        f"Total: ₹{order.total_amount}",
        f"Created: {timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')}",
        "Status: Pending",
    ]
    return "\n".join(lines)


def _format_user_status_message(order: Order) -> str:
    status_text = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'processing': 'Preparing',
        'ready_for_pickup': 'Ready for Pickup',
        'out_for_delivery': 'Out for Delivery',
        'picked_up': 'Completed',
        'cancelled': 'Cancelled',
    }.get(order.status, order.status)

    return (
        f"Hi {order.customer_name},\n"
        f"Your order #{order.id} status is now: {status_text}.\n"
        f"Total: ₹{order.total_amount}.\n"
        f"Pickup date: {order.pickup_date}.\n"
        f"Thank you for choosing Rose Cakes!"
    )


def notify_admin_new_order(order: Order) -> None:
    site = SiteSettings.get_settings()
    admin_email = site.email if site and site.email else getattr(settings, 'EMAIL_HOST_USER', None)
    admin_whatsapp = None
    if site and site.whatsapp_number:
        # Expect E.164 like +91XXXXXXXXXX; if stored locally without +, try to use as-is
        admin_whatsapp = site.whatsapp_number

    subject = f"New Order #{order.id} - Pending"
    body = _format_admin_new_order_message(order)
    _send_email(admin_email, subject, body)
    _send_whatsapp(admin_whatsapp, body)


def notify_user_order_status(order: Order) -> None:
    subject = f"Your Order #{order.id} Update"
    body = _format_user_status_message(order)
    _send_email(order.customer_email, subject, body)
    _send_whatsapp(order.whatsapp_number, body)


