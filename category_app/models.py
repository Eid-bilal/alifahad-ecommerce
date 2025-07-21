from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    UNIT_CHOICES = [
        ('ml', 'Milligram'),
        ('bottle', 'Bottle'),
        ('box', 'Box')
    ]

    category_name = models.CharField(max_length=255)
    category_image = CloudinaryField('image', blank=True, null=True)
    category_offer = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    is_listed = models.BooleanField(default=True)
    category_unit = models.CharField(max_length=50, choices=UNIT_CHOICES, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name