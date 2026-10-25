from django.shortcuts import render

# Create your views here.

from store.models import Product     # after (use YOUR app name)




# Three views:
#   CheckoutView      = creates the order and returns the Paystack payment link
#   VerifyPaymentView = confirms payment, sets delivery date, sends the receipt
#   OrderListView     = lists the logged-in user's paid orders

from datetime import timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Product  # change "products" to your app name
from .emails import send_receipt
from .models import Order, OrderItem, TrackingEvent
from .paystack import payment_is_successful, start_payment
from .serializers import OrderSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]  # no token = no order

    def post(self, request):
        items = request.data.get("items", [])        # [{id, quantity}, ...]
        shipping = request.data.get("shipping", {})  # delivery details

        if len(items) == 0:
            return Response({"detail": "Your cart is empty."}, status=400)

        # Paystack and the receipt both need the user's email
        if not request.user.email:
            return Response({"detail": "Your account has no email address."}, status=400)

        # 1. find each product in the DATABASE (never trust prices from React)
        products = []
        for item in items:
            product = get_object_or_404(Product, id=item["id"])
            products.append((product, int(item["quantity"])))

        # 2. work out the total
        total = sum(product.price * quantity for product, quantity in products)

        # 3. save the order
        order = Order.objects.create(
            user=request.user,
            total=total,
            first_name=shipping.get("first_name", ""),
            last_name=shipping.get("last_name", ""),
            address=shipping.get("address", ""),
            city=shipping.get("city", ""),
            state=shipping.get("state", ""),
            postal_code=shipping.get("postal_code", ""),
            phone=shipping.get("phone", ""),
        )

        # 4. save each product on the order
        for product, quantity in products:
            OrderItem.objects.create(
                order=order, product=product, name=product.name,
                quantity=quantity, price=product.price,
            )

        TrackingEvent.objects.create(order=order, status="pending", note="Order placed")

        # 5. get the Paystack payment link
        payment_link = start_payment(order, request.user.email)

        if payment_link is None:
            order.delete()  # no link, so don't keep a useless order
            return Response({"detail": "Could not start payment. Try again."}, status=502)

        return Response(
            {"authorization_url": payment_link, "reference": order.reference},
            status=201,
        )


class VerifyPaymentView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):
        # only the owner can verify their own order
        order = get_object_or_404(Order, reference=reference, user=request.user)
        

        if order.is_paid:  # already confirmed earlier (also stops a second email)
            return Response({"status": "success"})

        if payment_is_successful(order):
            order.is_paid = True
            order.status = "paid"
            # delivery date = today + DELIVERY_DAYS (set in settings.py)
            order.estimated_delivery = timezone.localdate() + timedelta(days=settings.DELIVERY_DAYS)
            order.save()
            TrackingEvent.objects.create(order=order, status="paid", note="Payment received")

            # send_receipt(order)  # email the receipt (a failed email never breaks the payment)
                        # a problem with the receipt must never break the payment
            try:
                send_receipt(order)
            except Exception as error:
                print("RECEIPT ERROR:", repr(error))
                
            return Response({"status": "success"})

        return Response({"status": "failed"}, status=400)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only THIS user's PAID orders, newest first
        return Order.objects.filter(user=self.request.user, is_paid=True).order_by("-created_at")