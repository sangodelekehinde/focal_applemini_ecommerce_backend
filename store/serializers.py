# create serializers
# from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'banner', 'description', 'price', 'image', 'stock', 'is_new']