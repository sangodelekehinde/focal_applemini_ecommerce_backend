from django.db import models

# Create your models here.
# Three tables:
#   Order         = the receipt
#   OrderItem     = each product on the receipt
#   TrackingEvent = each step in the delivery timeline

import uuid
from django.conf import settings
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending payment"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    # who placed the order
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    reference = models.CharField(max_length=100, unique=True, blank=True)  # id Paystack uses
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.DateField(null=True, blank=True)  # add this line

    # delivery details (from your Checkout form)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        # create a unique reference the first time the order is saved
        if not self.reference:
            self.reference = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.reference[:8]} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("store.Product", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)  # copied, so history stays if the product is deleted
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of purchase


class TrackingEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=20)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.DateField(null=True, blank=True)  # set when payment succeeds

    class Meta:
        ordering = ["created_at"]  # oldest first, like a timeline