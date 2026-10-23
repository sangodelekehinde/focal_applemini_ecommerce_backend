# Builds and sends the payment receipt email.

from django.conf import settings
from django.core.mail import send_mail


def send_receipt(order):
    """Email the receipt to the customer. Returns True if sent, False if it failed."""

    # one line per product, e.g. "- Round Glasses x2: ₦10000"
    lines = []
    for item in order.items.all():
        lines.append(f"- {item.name} x{item.quantity}: ₦{item.price * item.quantity}")
    items_text = "\n".join(lines)

    delivery_date = order.estimated_delivery.strftime("%A, %d %B %Y")

    message = f"""Hi {order.first_name},

Thank you for your order! Your payment was received.

Order reference: {order.reference[:8]}
Date: {order.created_at.strftime("%d %B %Y")}

Items:
{items_text}

Total paid: ₦{order.total}

Delivery address:
{order.address}, {order.city}, {order.state}
Estimated delivery: {delivery_date}

You can follow your order any time under Orders on our website.

{settings.STORE_NAME}
"""

    try:
        send_mail(
            subject=f"Your {settings.STORE_NAME} receipt - Order {order.reference[:8]}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],  # the email the user typed at signup
        )
        return True
    except Exception as error:
        print("Receipt email failed:", error)  # the order is still marked as paid
        return False