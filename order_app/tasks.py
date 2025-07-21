from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import Order
from .utils import generate_invoice

@shared_task
def send_purchase_email(user_id, order_id):
    from django.contrib.auth.models import User
    user = User.objects.get(id=user_id)
    order = Order.objects.get(serial_number=order_id)
    subject = 'Your Purchase Confirmation'
    message = f'Thank you for your purchase, {user.username}!\n\nYour order number is {order.serial_number}.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)

@shared_task
def send_invoice_email(user_id, order_id):
    from django.contrib.auth.models import User
    user = User.objects.get(id=user_id)
    order = Order.objects.get(serial_number=order_id)
    
    # Generate the invoice PDF
    invoice_path = generate_invoice(order)
    
    if invoice_path:
        subject = 'Your Purchase Invoice'
        message = f'Thank you for your purchase, {user.username}!\n\nPlease find your invoice attached.'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        email = EmailMessage(subject, message, email_from, recipient_list)
        email.attach_file(invoice_path)
        email.send()
