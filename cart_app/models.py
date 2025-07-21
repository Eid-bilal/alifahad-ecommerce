from django.db import models
from django.contrib.auth.models import User
from product_app.models import Product, Variant
from coupon_app.models import Coupon


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    variant = models.ForeignKey(
        Variant, on_delete=models.SET_NULL, null=True
    )

    def __str__(self) -> str:
        return f"{self.variant} on {self.added_on}"
    


class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    total_amount_without_coupon = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    coupon_active = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"'{self.user_id}'s cart"
    
    def remove_coupon(self):
        self.coupon = None
        self.coupon_active = False
        self.save()



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant.product.product_name} - {self.variant.size} x {self.quantity}"
    



