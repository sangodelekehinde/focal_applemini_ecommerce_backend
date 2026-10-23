# Turns database rows into JSON for React

from rest_framework import serializers
from .models import Order, OrderItem, TrackingEvent


class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source="product.image", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["name", "quantity", "price", "image"]


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = ["status", "note", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    events = TrackingEventSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "reference", "total", "status", "status_display", "is_paid",
            "created_at", "estimated_delivery",
            "address", "city", "state", "items", "events",
        ]