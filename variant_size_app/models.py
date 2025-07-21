from django.db import models
from category_app.models import Category
from django.core.exceptions import ValidationError

class VariantSize(models.Model):
    UNIT_CHOICES = (
        ('ml', 'Milligram'),
        ('bottle', 'Bottle'),
        ('box', 'Box')
    )

    size_name = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='g')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='variant_sizes')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('size_name', 'unit', 'category')  # Ensure unique combination

    def __str__(self):
        return f"{self.size_name} {self.unit} ({self.category.category_name})"
    
    def clean(self):
        if not self.size_name.replace('.', '', 1).isdigit():
            raise ValidationError("Size name must be a number (e.g., '100', '0.5').")