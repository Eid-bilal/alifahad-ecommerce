from django.db import models

# Create your models here.

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    code = models.CharField(max_length=30, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(choices=DISCOUNT_TYPE_CHOICES, max_length=20)
    min_purchase_amount = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    usage_limit = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code