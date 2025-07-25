# Generated by Django 5.1.4 on 2025-07-16 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0024_order_wallet_deduction'),
        ('user_profile_app', '0010_remove_userprofile_user_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_profile_app.address'),
        ),
    ]
