from django.contrib import admin
from .models import Product, Variant

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'is_listed', 'created_at')
    list_filter = ('category', 'is_listed')
    search_fields = ('product_name',)

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price', 'stock', 'featured')
    list_filter = ('product__category', 'featured')
    search_fields = ('product__product_name', 'size__size_name')