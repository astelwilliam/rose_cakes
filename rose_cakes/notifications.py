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
        f"🎂 NEW ORDER RECEIVED - Order #{order.id}",
        "",
        "Customer Details:",
        f"  Name: {order.customer_name}",
        f"  Email: {order.customer_email}",
        f"  WhatsApp: {order.whatsapp_number or 'Not provided'}",
        "",
        "Order Details:",
        f"  Pickup Date: {order.pickup_date}",
        f"  Total Amount: ₹{order.total_amount}",
        f"  Discount: ₹{order.discount_amount if order.discount_amount else 0}",
        f"  Order Date: {timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')}",
        "",
        "Order Items:",
    ]
    for item in order.items.all():
        lines.append(f"  • {item.cake.name} x{item.quantity} - ₹{item.price} each (Subtotal: ₹{item.price * item.quantity})")
    lines.extend([
        "",
        "Status: Pending - Awaiting Admin Confirmation",
        "",
        "Please log in to the admin panel to accept and process this order.",
    ])
    return "\n".join(lines)


def _format_user_status_message(order: Order) -> str:
    status_messages = {
        'pending': {
            'title': 'Order Received',
            'message': 'We have received your order and it is pending admin confirmation. You will be notified once it is confirmed.'
        },
        'confirmed': {
            'title': 'Order Confirmed! 🎉',
            'message': 'Great news! Your order has been confirmed and we have started preparing your delicious cakes.'
        },
        'processing': {
            'title': 'Order Being Prepared 👨‍🍳',
            'message': 'Your order is currently being prepared with love and care. We are working hard to make it perfect for you!'
        },
        'ready_for_pickup': {
            'title': 'Order Ready for Pickup! ✅',
            'message': 'Your order is ready for pickup! Please come to our store on your selected pickup date to collect your cakes.'
        },
        'out_for_delivery': {
            'title': 'Order Out for Delivery 🚚',
            'message': 'Your order is on the way! Please be available to receive your cakes.'
        },
        'picked_up': {
            'title': 'Order Completed! 🎂',
            'message': 'Thank you for choosing Rose Cakes! We hope you enjoy your delicious cakes. We look forward to serving you again!'
        },
        'cancelled': {
            'title': 'Order Cancelled',
            'message': 'Your order has been cancelled. If you have any questions, please contact us.'
        },
    }
    
    status_info = status_messages.get(order.status, {
        'title': 'Order Update',
        'message': f'Your order status has been updated to {order.status}.'
    })
    
    lines = [
        f"Hi {order.customer_name},",
        "",
        f"{status_info['title']}",
        "",
        f"Order #{order.id}",
        "",
        status_info['message'],
        "",
        "Order Summary:",
    ]
    for item in order.items.all():
        lines.append(f"  • {item.cake.name} x{item.quantity} - ₹{item.price * item.quantity}")
    lines.extend([
        "",
        f"Total Amount: ₹{order.total_amount}",
        f"Pickup Date: {order.pickup_date}",
        "",
        "Thank you for choosing Rose Cakes!",
        "",
        "If you have any questions, please contact us.",
    ])
    return "\n".join(lines)


def notify_admin_new_order(order: Order) -> None:
    site = SiteSettings.get_settings()
    admin_email = site.email if site and site.email else getattr(settings, 'EMAIL_HOST_USER', None)
    admin_whatsapp = None
    if site and site.whatsapp_number:
        # Expect E.164 like +91XXXXXXXXXX; if stored locally without +, try to use as-is
        admin_whatsapp = site.whatsapp_number

    subject = f"🎂 NEW ORDER #{order.id} - {order.customer_name} - ₹{order.total_amount} - Pending Confirmation"
    body = _format_admin_new_order_message(order)
    _send_email(admin_email, subject, body)
    _send_whatsapp(admin_whatsapp, body)


def notify_user_order_status(order: Order) -> None:
    status_subjects = {
        'pending': 'Order Received - Rose Cakes',
        'confirmed': 'Order Confirmed - Rose Cakes',
        'processing': 'Your Order is Being Prepared - Rose Cakes',
        'ready_for_pickup': 'Order Ready for Pickup - Rose Cakes',
        'out_for_delivery': 'Order Out for Delivery - Rose Cakes',
        'picked_up': 'Order Completed - Thank You! - Rose Cakes',
        'cancelled': 'Order Cancelled - Rose Cakes',
    }
    subject = status_subjects.get(order.status, f"Order #{order.id} Update - Rose Cakes")
    body = _format_user_status_message(order)
    _send_email(order.customer_email, subject, body)
    _send_whatsapp(order.whatsapp_number, body)


