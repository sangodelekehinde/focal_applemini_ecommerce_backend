from django.db import models

# Create your models here.

# created product models

# from django.db import models



class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_new = models.BooleanField(default=False)
    banner = models.ImageField(upload_to='products/banners/', blank=True, null=True)  # large detail-page image
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name




# 

from django.contrib.auth.models import User


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("store.Product", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "product")