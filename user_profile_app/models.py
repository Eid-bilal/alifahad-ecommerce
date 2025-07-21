from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver

class Address(models.Model):
    user = models.ForeignKey(User, related_name='profile', on_delete=models.CASCADE)
    delete_address = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50, default="Not Added")
    landmark = models.CharField(max_length=30, blank=True, null=True)
    address_type = models.CharField(max_length=10, default="Home")
    accessible = models.CharField(max_length=50, default="Not Added")
    area = models.CharField(max_length=50, default="Not Added")
    city = models.CharField(max_length=50, default="Not Added")
    pincode_regex = RegexValidator(regex=r"^\d{6}$", message="Pincode must be 6 digits")
    pincode = models.CharField(max_length=6, validators=[pincode_regex], default="000000")
    post_office = models.CharField(max_length=40, default="Not Added")
    state = models.CharField(max_length=40, default="Not Added")
    phone_regex = RegexValidator(regex=r"^\d{10}$", message="Phone number must be 10 digits")
    phone_no = models.CharField(max_length=10, validators=[phone_regex], default="0000000000")
    alternative_phone = models.CharField(max_length=10, validators=[phone_regex], blank=True, null=True)
    

    def __str__(self):
        return self.user.username

class Referral(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=160, unique=True)

    def __str__(self):
        return self.referral_code

def generate_referral_code(username):
    random_number = "".join(random.choices(string.digits, k=5))
    return f"{username}{random_number}"

@receiver(post_save, sender=User)
def create_referral(sender, instance, created, **kwargs):
    if created:
        referral_code = generate_referral_code(instance.username)
        while Referral.objects.filter(referral_code=referral_code).exists():
            referral_code = generate_referral_code(instance.username)
        Referral.objects.create(user=instance, referral_code=referral_code)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Address.objects.create(user=instance)