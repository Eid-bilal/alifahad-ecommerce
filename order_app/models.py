from django.db import models
from django.contrib.auth.models import User
from product_app.models import Variant

# from coupons_app.models import Coupons
from user_profile_app.models import Address
from django.utils import timezone


# Create your models here.


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        ('wallet', 'Wallet'),
        ('split', 'Split Payment'),

    ]

    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ("Pending", "Order Pending"),
        ("Processing", "Processing"),
        ("Confirmed", "Order confirmed"),
        ("Shipped", "Shipped"),
        ("Out For Delivery", "Out For Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    )

    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.AutoField(primary_key=True, unique=True, editable=False)
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_method = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    payment_online_id = models.CharField(
        max_length=50, default="0000", null=True, blank=True
    )
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default="Pending")
    order_date = models.DateTimeField(auto_now_add=True)
    coupon_name = models.CharField(max_length=255, null=True, blank=True)
    coupon_discount = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_return_requested = models.BooleanField(default=False)
    wallet_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            max_serial_number = Order.objects.aggregate(models.Max("serial_number"))[
                "serial_number__max"
            ]
            if max_serial_number is not None:
                self.serial_number = max_serial_number + 1
            else:
                self.serial_number = 100001
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.serial_number}"


class OrderItems(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Order Pending"),
        ("Processing", "Processing"),
        ("Confirmed", "Order confirmed"),
        ("Shipped", "Shipped"),
        ("Out For Delivery", "Out For Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
        ("Requested", "Requested"),

    )

    order = models.ForeignKey(
        Order, related_name="order_all", on_delete=models.CASCADE, null=True, blank=True
    )
    product_added = models.ForeignKey(
        Variant, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.IntegerField(default=00)
    size = models.CharField(max_length=255, default="toadd")
    last_update = models.DateTimeField(auto_now=True)
    final_product_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=False, default=0.00
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="Pending")
    item_return_requested = models.BooleanField(default=False)
    accept_order = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.order} ,PK{self.pk}"

    def expected_delivery_date(self):
        self.expected_date = self.order.order_date + timezone.timedelta(days=10)
        return self.expected_date


class CancelledOrder(models.Model):
    ordered_item = models.ForeignKey(OrderItems, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(null=True, blank=True)
    request_date = models.DateField(auto_now_add=True, null=True)
    pickup_date = models.DateField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    def __str__(self) -> str:
        s = f" Order_id = {self.ordered_item.pk}"
        x = f", return status = {self.ordered_item.status}"
        return s + x

    

        


