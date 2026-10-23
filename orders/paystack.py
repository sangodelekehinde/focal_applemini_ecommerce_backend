# All talking to Paystack lives here, so views.py stays simple.

import requests
from django.conf import settings

HEADERS = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}


def start_payment(order, email):
    """Ask Paystack for a payment link. Returns the link, or None if it failed."""
    try:
        res = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=HEADERS,
            json={
                "email": email,
                "amount": int(order.total * 100),  # Paystack counts in kobo, so x100
                "currency": "NGN",
                "reference": order.reference,
                "callback_url": f"{settings.FRONTEND_URL}/payment/callback",
            },
            timeout=20,
        ).json()
    except (requests.RequestException, ValueError):
        return None

    if res.get("status"):
        return res["data"]["authorization_url"]
    return None


def payment_is_successful(order):
    """Ask Paystack if this order was really paid. Returns True or False."""
    try:
        res = requests.get(
            f"https://api.paystack.co/transaction/verify/{order.reference}",
            headers=HEADERS,
            timeout=20,
        ).json()
    except (requests.RequestException, ValueError):
        return False

    data = res.get("data") or {}
    return (
        res.get("status") is True
        and data.get("status") == "success"
        and data.get("amount") == int(order.total * 100)  # amount paid must match
    )