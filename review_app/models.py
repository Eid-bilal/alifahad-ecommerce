from django.db import models
from django.contrib.auth.models import User
from product_app.models import Product

# Create your models here.

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name} - {self.score}'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, related_name='reviews', null=True)
    score = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)], null=True)
    title = models.CharField(max_length=200, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'