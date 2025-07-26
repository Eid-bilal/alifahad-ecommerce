from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings
from . models import  OTP
# from django.contrib.auth.backends import ModelBackend
# import random
from django.http import JsonResponse
from django.contrib.auth import login
# import re
# import random
from django.http import JsonResponse
from category_app.models import Category
from product_app.models import Product
# from .forms import CustomSignupForm
from django.core.paginator import Paginator
import datetime
from django.urls import reverse
from django.db import models




# Create your views here.

def redirect_to_home(request):
    return redirect('user/login')

#=========================================================================================================================#
@never_cache
@login_required
def user_home(request):
    # Fetch listed categories and products
    categories = Category.objects.filter(is_listed=True)
    products = Product.objects.filter(is_listed=True, category__is_listed=True).order_by('-created_at')

    # Handle search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(product_name__icontains=query)

    # Handle category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__category_name__iexact=category_filter)

    # Handle sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'popularity':
        products = products.annotate(variant_count=Count('variants')).order_by('-variant_count')
    elif sort_by == 'price_low_high':
        products = products.order_by('variants__price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-variants__price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created_at')
    elif sort_by == 'a_to_z':
        products = products.order_by('product_name')
    elif sort_by == 'z_to_a':
        products = products.order_by('-product_name')

    # Paginate products
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user/home.html', {
        'categories': categories,
        'products': page_obj,
        'query': query,
        'sort_by': sort_by,
        'category_filter': category_filter,
    })

#=========================================================================================================================#
def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, is_listed=True)  # Filter active products
    return render(request, 'user/category_products.html', {'category': category, 'products': products})

#=========================================================================================================================#

def shop(request):
    products = Product.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(product_name__icontains=query)

    return render(request, 'user/shop.html', {
        'products': products,
        'query': query
    })
#=========================================================================================================================#

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import OTP, Profile
from django.utils import timezone
from datetime import timedelta
import random
import re
import os

def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    sender_email = os.getenv('EMAIL_HOST_USER')
    try:
        send_mail(subject, message, sender_email, [email])
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def validate_mobile(mobile):
    if not re.match(r"^\+?\d{10,15}$", mobile):
        return False, "Enter a valid mobile number."
    return True, ""

def user_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        mobile = request.POST.get('mobile', '').strip()

        # Validation
        errors = {}

        # Username validation
        if not username or len(username) < 3:
            errors['username_error'] = "Username must be at least 3 characters long."
        elif User.objects.filter(username=username).exists():
            errors['username_error'] = "Username is already taken."

        # Email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors['email_error'] = "Enter a valid email address."
        elif User.objects.filter(email=email).exists():
            errors['email_error'] = "Email is already registered."

        # Password validation
        password_valid, password_error = validate_password(password)
        if not password_valid:
            errors['password_error'] = [password_error]
        elif password != confirm_password:
            errors['password_error'] = ["Passwords do not match."]

        # Mobile number validation
        mobile_valid, mobile_error = validate_mobile(mobile)
        if not mobile_valid:
            errors['mobile_number_error'] = mobile_error

        if errors:
            return render(request, 'user/signup.html', {
                'errors': errors,
                'username': username,
                'email': email,
                'mobile': mobile,
            })

        # Save data to session and send OTP
        try:
            otp = generate_otp()
            print(otp)
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Create or update OTP
            OTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'expires_at': expires_at}
            )
            print("otp created")

            # Send OTP email
            if not send_otp_email(email, otp):
                errors['email_error'] = "Failed to send OTP email. Please try again."
                return render(request, 'user/signup.html', {
                    'errors': errors,
                    'username': username,
                    'email': email,
                    'mobile': mobile,
                })
            

            # Store user information in session
            request.session['registration_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'mobile': mobile,
            }

            return redirect('verify_otp', email=email)

        except Exception as e:
            print(e)
            errors['general_error'] = "An error occurred. Please try again."
            return render(request, 'user/signup.html', {
                'errors': errors,
                'username': username,
                'email': email,
                'mobile': mobile,
            })

    return render(request, 'user/signup.html')

#================================================================================================================

from django.contrib.auth import login

def verify_otp(request, email):
    # Check if session data exists
    if not request.session.get('registration_data'):
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            otp_instance = OTP.objects.get(email=email)

            # Check if OTP is expired
            if otp_instance.is_expired():
                return render(request, 'user/verify_otp.html', {
                    'email': email,
                    'error': 'OTP has expired. Please request a new one.'
                })

            # Validate OTP
            if str(otp_instance.otp) == entered_otp:
                # Retrieve registration data from session
                registration_data = request.session['registration_data']
                
                # Create user
                user = User.objects.create_user(
                    username=registration_data['username'],
                    email=registration_data['email'],
                    password=registration_data['password']
                )

                # Create Profile instance and link the mobile number
                Profile.objects.create(user=user, mobile=registration_data['mobile'])

                # Clean up
                del request.session['registration_data']
                otp_instance.delete()

                # Log the user in
                login(request, user)

                return redirect('home')
            else:
                return render(request, 'user/verify_otp.html', {
                    'email': email,
                    'error': 'Invalid OTP. Please try again.'
                })

        except OTP.DoesNotExist:
            return render(request, 'user/verify_otp.html', {
                'email': email,
                'error': 'OTP not found. Please register again.'
            })

    return render(request, 'user/verify_otp.html', {'email': email})

#=================================================================================================================================
import random
import string
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

def generate_otp(length=6):
    """Generate a random numeric OTP of specified length."""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def resend_otp(request, email):
    if request.method == 'POST':
        print('hai')
        try:
            otp_instance = OTP.objects.filter(email=email).first()
            if otp_instance:
                time_elapsed = timezone.now() - otp_instance.updated_at
                if time_elapsed < timedelta(seconds=30):
                    return JsonResponse({
                        'success': False,
                        'message': f'Please wait {30 - time_elapsed.seconds}s before requesting a new OTP.'
                    })
        
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            print(otp)  # For debugging; remove in production
            OTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'expires_at': expires_at}
            )

            if send_otp_email(email, otp):
                return JsonResponse({'success': True, 'message': 'New OTP sent successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to send OTP. Try again.'})                

        except Exception as e:
            print(e)  # For debugging; use proper logging in production
            return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

#====================================================================================================================

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.management.utils import get_random_secret_key

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return render(request, 'user/login.html', {
                'error': 'Please enter both username and password.'
            })
        
        
        print('My new secret key:',get_random_secret_key())

        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            # Check if the user is active
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'user/login.html', {
                    'error': 'Your account is blocked. Please contact support.'
                })
        else:
            return render(request, 'user/login.html', {
                'error': 'Invalid username or password.',
                'username': username
            })

    return render(request, 'user/login.html')
#================================================================================================================

# In your views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirects to the homepage or any other page

#=====================================================================================================
import re
import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User

def generate_otp(length=6):
    """
    Generate a random OTP of specified length.
    
    Args:
        length (int): Length of OTP. Defaults to 6.
    
    Returns:
        str: Generated OTP
    """
    import random
    return ''.join(random.choices('0123456789', k=length))

@never_cache
def forgot_password(request):
    """
    Handle forgot password functionality with email verification.
    
    Args:
        request (HttpRequest): Django request object
    
    Returns:
        JsonResponse or HttpResponse: Response based on request method and validation
    """
    # Prevent authenticated users from accessing forgot password
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Retrieve email from POST data
        email = request.POST.get('email', '').strip()
        errors = {}

        # Email validation regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        # Validate email
        if not re.match(email_pattern, email):
            errors['email_error'] = 'Invalid email format'
        elif not User.objects.filter(email=email).exists():
            errors['email_error'] = 'Email does not exist'

        # If there are validation errors, return JSON error response
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        # Generate OTP
        otp = generate_otp()

        # Set OTP expiry (5 minutes from now)
        otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        # Store OTP details in session
        request.session['otp'] = otp
        request.session['otp_expiry'] = otp_expiry.timestamp()
        request.session['email'] = email

        # Send OTP via email
        try:
            send_mail(
                'Password Reset OTP',
                f'Your OTP code is {otp}. This code will expire in 5 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error in a real-world scenario
            return JsonResponse({
                'status': 'error', 
                'errors': {'email_error': 'Failed to send OTP. Please try again.'}
            }, status=500)

        # Successful OTP generation and email sending
        return redirect('otp_verify')

    # Render forgot password template for GET requests
    return render(request, 'user/forgot/forgot_password.html')
#------------------------------------------------------------------------------------------------------------------------
@never_cache
def otp_verify(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')  
        otp_expiry = request.session.get('otp_expiry')

        errors = {}

        if not session_otp or not otp_expiry:
            errors['otp'] = 'OTP session has expired. Please request a new OTP.'
        elif datetime.datetime.now().timestamp() > otp_expiry:
            errors['otp'] = 'OTP has expired. Please request a new one.'
        elif entered_otp != str(session_otp):
            errors['otp'] = 'Invalid OTP entered. Please try again.'

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
        
        # OTP is valid — clear session and respond with redirect target
        try:
            del request.session['otp']
            del request.session['otp_expiry']
        except KeyError:
            pass

        return JsonResponse({
            'status': 'success',
            'redirect_url': '/reset-password/'  # or use reverse('reset_new_password')
        })

    # If GET request, render the template
    return render(request, 'user/forgot/reset_otp.html')
#----------------------------------------------------------------------------------------------------------------------------
def reset_resend_otp(request):
    email = request.session.get('email')  # Retrieve email from session

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please sign up again.'}, status=400)

    if request.method == 'POST':
        new_otp = generate_otp() 
        request.session['otp'] = new_otp
        request.session['otp_expiry'] = (datetime.datetime.now() + datetime.timedelta(minutes=1)).timestamp()

        try:
            send_mail(
                'Your New OTP Code',
                f'Your new OTP code is {new_otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print(f"Forgot Resent otp: {new_otp}")
            return JsonResponse({'status': 'success', 'message': 'A new OTP has been sent to your email.'})
            
    
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to resend OTP. Please try again.'}, status=500)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
   
#----------------------------------------------------------------------------------------------------------------------------
@never_cache
def reset_new_password(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        new_password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        
        errors = {}

        if new_password != confirm_password:
            errors['password_error'] = 'Passwords do not match.'
        if len(new_password) < 6:  # You can adjust the password policy as needed
            errors['password_error'] = 'Password must be at least 6 characters long.'
        if not re.search(r'[A-Z]', new_password):
            errors.setdefault('password_error', []).append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', new_password):
            errors.setdefault('password_error', []).append('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', new_password):
            errors.setdefault('password_error', []).append('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            errors.setdefault('password_error', []).append('Password must contain at least one special character')

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        # Assuming the user is identified by their email session or another means
        email = request.session.get('email')  # Ensure you set this during OTP generation
        user = User.objects.get(email=email)
        user.set_password(new_password)  # Use Django's built-in method to hash the password
        user.save()

        del request.session['otp']
        del request.session['otp_expiry']

        # return JsonResponse({'status': 'success', 'redirect_url': reverse('login')})
        return redirect('login')

    return render(request, 'user/forgot/reset_forgot_pass.html')
#----------------------------------------------------------------------------------------------------------------------------