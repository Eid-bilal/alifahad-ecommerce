from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField
import random



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='phone')
    mobile = models.CharField(max_length=15, blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True,default='profile_default')

    def __str__(self):
        return f"{self.user.username}'s Profile"



    
    
class OTP(models.Model):
    email = models.EmailField(unique=True,null=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    # def is_valid(self):
    #     return self.created_at >= timezone.now() - timedelta(minutes=10)

    # def save(self, *args, **kwargs):
    #     if not self.otp:
    #         self.otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f'{self.user.username} - {self.otp}'
    
    def is_expired(self):
        return timezone.now() > self.expires_at




