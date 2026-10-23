from django.contrib import admin

# Register your models here.


# Lets you change an order's status in Django admin.
# Changing the status automatically adds a tracking event.

from django.contrib import admin
from .models import Order, OrderItem, TrackingEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "user", "status", "is_paid", "estimated_delivery", "created_at"]
    inlines = [OrderItemInline, TrackingEventInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and "status" in form.changed_data:
            TrackingEvent.objects.create(
                order=obj, status=obj.status,
                note=f"Order is now {obj.get_status_display()}",
            )