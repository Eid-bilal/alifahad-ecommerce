from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from category_app.models import Category
from variant_size_app.models import VariantSize

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_1 = CloudinaryField('image')
    image_2 = CloudinaryField('image', blank=True, null=True)
    image_3 = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(blank=False, default=True)
    delete_opt = models.BooleanField(blank=False, default=False)
    offer_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )

    def save(self, *args, **kwargs):
        if self.category:
            self.unit = self.category.category_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.ForeignKey(VariantSize, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    offer_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(blank=False, default=False)

    def product_price_after(self):
        variant_offer = self.offer_percentage
        product_offer = self.product.offer_percentage
        category_offer = self.product.category.category_offer
        highest_offer = max(variant_offer, product_offer, category_offer)
        discounted_price = self.price - (highest_offer * self.price / 100)
        return round(discounted_price, 2)

    def __str__(self):
        return f"{self.product.product_name} - {self.size.size_name}"