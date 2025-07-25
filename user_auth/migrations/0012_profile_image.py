# Generated by Django 5.1.4 on 2025-07-16 13:44

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0011_alter_otp_expires_at_alter_otp_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, default='profile_default', max_length=255, null=True, verbose_name='image'),
        ),
    ]
