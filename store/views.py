from django.shortcuts import render

from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

# Create your views here.



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer




# serialized cart item

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CartItem


def serialize_cart(user):
    items = user.cart_items.select_related("product")
    return [
        {
            "id": i.product.id,
            "name": i.product.name,
            "price": i.product.price,
            "quantity": i.quantity,
        }
        for i in items
    ]


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == "PUT":
        with transaction.atomic():
            request.user.cart_items.all().delete()
            for item in request.data.get("items", []):
                CartItem.objects.create(
                    user=request.user,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                )
    return Response(serialize_cart(request.user))