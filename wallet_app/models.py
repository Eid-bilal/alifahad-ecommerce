from django.db import models
from django.contrib.auth.models import User
from order_app.models import Order
from django.db import transaction




# Create your models here.


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="wallet")
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user}, {self.balance}"
    


class WalletTransactions(models.Model):

    SPENT = 'spent'
    EARNED = 'earned'
    REFUND = 'refund'
    SPIN = 'spin'

    TRANSACTION_TYPES = [
        (SPENT, 'Spent'),
        (EARNED, 'Earned'),
        (REFUND, 'Refund'),
        (SPIN, 'Spin Reward')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, null=True)
    description = models.TextField(default=None)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} - {self.timestamp}"




class SpinHistory(models.Model):
    """Model to track user spin history and rewards"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward_amount = models.FloatField()
    spin_date = models.DateTimeField(auto_now_add=True)
    is_won = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - ${self.reward_amount} - {self.spin_date}"