import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

class WhatsAppService:
    def __init__(self):
        # Get Twilio credentials from environment variables
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

        if self.account_sid and self.auth_token and self.whatsapp_number:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Warning: Twilio credentials not found. WhatsApp messaging disabled.")

    def send_message(self, to_number, message):
        """
        Send WhatsApp message to a customer
        """
        if not self.client:
            print(f"WhatsApp disabled - would send to {to_number}: {message}")
            return False

        try:
            # Format number with country code if not present
            if not to_number.startswith('+'):
                to_number = f"+91{to_number}"  # Assuming Indian numbers

            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_number}",
                body=message,
                to=f"whatsapp:{to_number}"
            )
            print(f"WhatsApp message sent successfully: {message.sid}")
            return True
        except TwilioException as e:
            print(f"Failed to send WhatsApp message: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending WhatsApp message: {e}")
            return False

    def send_order_status_update(self, order):
        """
        Send order status update to customer
        """
        if not order.whatsapp_number:
            print(f"No WhatsApp number for order {order.id}")
            return False

        status_messages = {
            'pending': f"🕒 Order #{order.id} Accepted!\n\nHi {order.customer_name},\n\nThank you for your order! Your order has been accepted and is being processed.\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Pickup Date: {order.pickup_date}\n\nWe'll notify you when your order is ready for pickup.\n\nRose Cakes Team",

            'confirmed': f"✅ Order #{order.id} Confirmed!\n\nHi {order.customer_name},\n\nYour order has been confirmed! We're preparing your delicious cakes.\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Pickup Date: {order.pickup_date}\n\nEstimated preparation time: 2-3 hours.\n\nRose Cakes Team",

            'processing': f"👨‍🍳 Order #{order.id} is Being Prepared!\n\nHi {order.customer_name},\n\nYour cakes are now being prepared by our expert bakers. We're putting extra love into making your order perfect!\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Pickup Date: {order.pickup_date}\n\nWe'll let you know when it's ready for pickup.\n\nRose Cakes Team",

            'ready_for_pickup': f"🎂 Order #{order.id} Ready for Pickup!\n\nHi {order.customer_name},\n\nYour delicious cakes are ready! Please come to collect your order.\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Pickup Date: {order.pickup_date}\n\n📍 Rose Cakes Store\n⏰ Store Hours: 9 AM - 9 PM\n\nPlease bring this message or mention order #{order.id} when picking up.\n\nRose Cakes Team",

            'out_for_delivery': f"🚚 Order #{order.id} Out for Delivery!\n\nHi {order.customer_name},\n\nYour order is on the way! Our delivery partner will reach you soon.\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Delivery Date: {order.pickup_date}\n\n📱 Track your order: [Tracking Link]\n\nThank you for choosing Rose Cakes!\n\nRose Cakes Team",

            'picked_up': f"✅ Order #{order.id} Picked Up Successfully!\n\nHi {order.customer_name},\n\nThank you for picking up your order! We hope you enjoy your delicious cakes.\n\nOrder Details:\n• Total: ₹{order.total_amount}\n• Pickup Date: {order.pickup_date}\n\n⭐ Please rate your experience and leave a review!\n\nVisit us again soon!\nRose Cakes Team",

            'cancelled': f"❌ Order #{order.id} Cancelled\n\nHi {order.customer_name},\n\nWe're sorry to inform you that your order has been cancelled.\n\nOrder Details:\n• Order ID: #{order.id}\n• Total: ₹{order.total_amount}\n\nIf you have any questions or need assistance, please contact us.\n\nRose Cakes Team"
        }

        message = status_messages.get(order.status, f"Order #{order.id} Status Update: {order.status}")
        return self.send_message(order.whatsapp_number, message)

    def send_order_confirmation(self, order):
        """
        Send order confirmation message
        """
        if not order.whatsapp_number:
            return False

        items_text = ""
        for item in order.items.all():
            items_text += f"• {item.cake.name} x{item.quantity} - ₹{item.price * item.quantity}\n"

        message = f"""🎂 Order Confirmed! #{order.id}

Hi {order.customer_name},

Thank you for choosing Rose Cakes! Your order has been confirmed.

📋 Order Details:
{items_text}
💰 Total: ₹{order.total_amount}
📅 Pickup Date: {order.pickup_date}

⏱️ Estimated preparation time: 2-3 hours
📍 Store Location: [Your Store Address]

We'll send you updates as your order progresses. For any questions, reply to this message.

Rose Cakes Team
🍰 Making Sweet Memories"""

        return self.send_message(order.whatsapp_number, message)

# Global instance
whatsapp_service = WhatsAppService()
