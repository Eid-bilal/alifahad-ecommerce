from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Address, Referral
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from validator_app import views

from wallet_app.models import Wallet, WalletTransactions
from order_app.models import Order

# Create your views here.

from user_auth.models import Profile  # Import Profile model

@login_required
@never_cache
def user_profile(request):
    storage = messages.get_messages(request)
    storage.used = True
    user_obj = request.user 
    print(user_obj)
    referral = get_object_or_404(Referral, user = user_obj)
    
    # Get user addresses
    try:
        addresses = Address.objects.filter(user=user_obj, delete_address=False)
    except Address.DoesNotExist:
        addresses = None

    # Get profile image from Profile model
    try:
        profile = Profile.objects.get(user=user_obj)  # Fetch Profile for the user
        profile_image = profile.image  # Access the CloudinaryField 'image'
    except Profile.DoesNotExist:  # Corrected to Profile.DoesNotExist
        profile_image = None  # Fallback if no Profile exists

    # Get user orders
    try:
        orders = Order.objects.filter(user_id=user_obj).order_by('-order_date')
    except Order.DoesNotExist:
        orders = None

    # Get wallet details
    try:
        wallet = Wallet.objects.get(user=user_obj)
        wallet_balance = wallet.balance
        last_transaction = WalletTransactions.objects.filter(wallet=wallet).order_by('-timestamp').first()
    except Wallet.DoesNotExist:
        wallet_balance = 0.00
        last_transaction = None

    context = {
        'user_details': user_obj,
        'user_address_details': addresses,
        'profile_image': profile_image,  # Uses Profile model's image
        'orders': orders,
        'wallet': {
            'balance': wallet_balance,
            'last_transaction': last_transaction
        
        },
        'referral': referral

    }

    return render(request, 'user/profile_user.html', context)

#-------------------------------------------- User Editing Profile ------------------------------------------------------#

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from user_profile_app.models import Address
import re
import cloudinary.uploader
import base64
import io

@login_required
def edit_profile(request):
    messages.get_messages(request).used = True
    user = request.user

    if request.method == "POST":
        user_username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        cropped_photo = request.POST.get("cropped_photo")

        try:
            # Username validation
            if User.objects.exclude(pk=user.pk).filter(username=user_username).exists():
                raise PermissionDenied("Username already taken.")
            check_username = username_test(user_username)
            if check_username[0]:
                raise ValidationError(check_username[1])

            # Email validation
            if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                raise PermissionDenied("Email already taken.")
            check_email = email_test(email)
            if check_email[0]:
                raise ValidationError(check_email[1])

            # Name validation
            if first_name:
                check_first_name = name_validator(first_name)
                if check_first_name[0]:
                    raise ValidationError(check_first_name[1])
                user.first_name = first_name
            if last_name:
                check_last_name = name_validator(last_name)
                if check_last_name[0]:
                    raise ValidationError(check_last_name[1])
                user.last_name = last_name

            # Update user fields
            user.username = user_username
            user.email = email
            user.save()

            # Handle profile image
            profile, created = Profile.objects.get_or_create(user=user)

            if cropped_photo and cropped_photo.startswith('data:image'):
                try:
                    format, imgstr = cropped_photo.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data = base64.b64decode(imgstr)
                    upload_result = cloudinary.uploader.upload(
                        io.BytesIO(img_data),
                        resource_type="image",
                        folder="user_profiles",
                        public_id=f"profile_{user.username}_{user.pk}"
                    )
                    profile.image = upload_result['public_id']
                    
                    profile.save()
                except Exception as e:
                    raise ValidationError(f"Failed to upload image: {str(e)}")

            messages.success(request, f"Updated {user_username} successfully")
            return redirect("user_profile")

        except PermissionDenied as e:
            messages.error(request, f"Error: {str(e)}")
        except ValidationError as v:
            messages.error(request, f"Error: {str(v)}")

    context = {"user_details": user}
    return render(request, "user/profile_edit.html", context)

@login_required
def add_address(request):
    storage = messages.get_messages(request)
    storage.used = True
    user = request.user

    if request.method == "POST":
        username = request.user.username
        user_data = User.objects.get(username=username)

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        alt_phone = request.POST.get("alt_ph")
        pincode = request.POST.get("pincode")
        post_office = request.POST.get("post_office")
        landmark = request.POST.get("landmark")
        accessible = request.POST.get("accessible")
        address_type = request.POST.get("address_type")
        area = request.POST.get("area")
        state = request.POST.get("state")
        city = request.POST.get("city")

        # Validate fields
        check_full_name = name_validator(full_name)
        check_post_office = validate_post_office_name(post_office)
        check_pin = validate_pin_code(pincode)
        check_landmark = validate_landmark(landmark)
        check_accessible = validate_area(accessible)
        check_area = validate_area(area)
        check_city = validate_city(city)
        check_state = validate_state(state)
        check_phone = validate_phone(phone)
        check_alt_phone = validate_phone(alt_phone)

        # Handle validation errors
        if check_full_name[0]:
            messages.error(request, check_full_name[1])
            return redirect("add_address")
        if check_post_office[0]:
            messages.error(request, check_post_office[1])
            return redirect("add_address")
        if check_pin[0]:
            messages.error(request, check_pin[1])
            return redirect("add_address")
        if check_landmark[0]:
            messages.error(request, check_landmark[1])
            return redirect("add_address")
        if check_accessible[0]:
            messages.error(request, check_accessible[1])
            return redirect("add_address")
        if check_area[0]:
            messages.error(request, check_area[1])
            return redirect("add_address")
        if check_city[0]:
            messages.error(request, check_city[1])
            return redirect("add_address")
        if check_state[0]:
            messages.error(request, check_state[1])
            return redirect("add_address")
        if check_phone[0]:
            messages.error(request, check_phone[1])
            return redirect("add_address")
        if check_alt_phone[0]:
            messages.error(request, check_alt_phone[1])
            return redirect("add_address")

        data = Address(
            user=user_data,
            pincode=pincode,
            post_office=post_office,
            landmark=landmark or None,
            accessible=accessible,
            address_type=address_type,
            area=area,
            state=state,
            city=city,
            alternative_phone=alt_phone or '',
            phone_no=phone,
            full_name=full_name,
            delete_address=False
        )
        try:
            data.full_clean()
            data.save()
            messages.success(request, "Address added")
            return redirect("user_profile")
        except Exception as e:
            messages.error(request, f"Error! {e}")

    return render(request, "user/address_add.html")

def username_test(username):
    """
    Validate username: must be 3-30 characters, alphanumeric with underscores/hyphens.
    Returns (is_invalid, error_message).
    """
    if not username:
        return (True, "Username is required.")
    if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', username):
        return (True, "Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens.")
    return (False, "")

def email_test(email):
    """
    Validate email format.
    Returns (is_invalid, error_message).
    """
    if not email:
        return (True, "Email is required.")
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return (True, "Invalid email format.")
    return (False, "")

def name_validator(name):
    """
    Validate name: must be 1-50 characters, letters, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not name:
        return (True, "Full name is required.")  # Modified for add_address
    if not re.match(r'^[a-zA-Z\s-]{1,50}$', name):
        return (True, "Name must be 1-50 characters and contain only letters, spaces, or hyphens.")
    return (False, "")

def validate_post_office_name(post_office):
    """
    Validate post office name: must be 1-40 characters, letters, numbers, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not post_office:
        return (True, "Post office name is required.")
    if not re.match(r'^[a-zA-Z0-9\s-]{1,40}$', post_office):
        return (True, "Post office name must be 1-40 characters and contain only letters, numbers, spaces, or hyphens.")
    return (False, "")

def validate_pin_code(pincode):
    """
    Validate pincode: must be exactly 6 digits.
    Returns (is_invalid, error_message).
    """
    if not pincode:
        return (True, "Pincode is required.")
    if not re.match(r'^\d{6}$', pincode):
        return (True, "Pincode must be exactly 6 digits.")
    return (False, "")

def validate_landmark(landmark):
    """
    Validate landmark: optional, max 30 characters, letters, numbers, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not landmark:
        return (False, "")  # Landmark is optional
    if not re.match(r'^[a-zA-Z0-9\s-]{0,30}$', landmark):
        return (True, "Landmark must be up to 30 characters and contain only letters, numbers, spaces, or hyphens.")
    return (False, "")

def validate_area(area):
    """
    Validate area/accessible: must be 1-50 characters, letters, numbers, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not area:
        return (True, "Area/Accessible is required.")
    if not re.match(r'^[a-zA-Z0-9\s-]{1,50}$', area):
        return (True, "Area/Accessible must be 1-50 characters and contain only letters, numbers, spaces, or hyphens.")
    return (False, "")

def validate_city(city):
    """
    Validate city: must be 1-50 characters, letters, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not city:
        return (True, "City is required.")
    if not re.match(r'^[a-zA-Z\s-]{1,50}$', city):
        return (True, "City must be 1-50 characters and contain only letters, spaces, or hyphens.")
    return (False, "")

def validate_state(state):
    """
    Validate state: must be 1-40 characters, letters, spaces, or hyphens.
    Returns (is_invalid, error_message).
    """
    if not state:
        return (True, "State is required.")
    if not re.match(r'^[a-zA-Z\s-]{1,40}$', state):
        return (True, "State must be 1-40 characters and contain only letters, spaces, or hyphens.")
    return (False, "")

def validate_phone(phone):
    """
    Validate phone: must be exactly 10 digits, optional for alt_phone.
    Returns (is_invalid, error_message).
    """
    if not phone:
        return (True, "Phone number is required.")  # Modified for main phone
    if not re.match(r'^\d{10}$', phone):
        return (True, "Phone number must be exactly 10 digits.")
    return (False, "")

#-------------------------------------------- User Editing Address -------------------------------------------------------#

@login_required
def edit_address(request, address_id):
    storage = messages.get_messages(request)
    storage.used = True

    addresses = UserProfile.objects.get(id=address_id)
    context = {
        "user_details": addresses,
    }
    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        alt_phone = request.POST.get("alt_ph")
        pincode = request.POST.get("pincode")
        post_office = request.POST.get("post_office")
        landmark = request.POST.get("landmark")
        accessible = request.POST.get("accessible")
        address_type = request.POST.get("address_type")
        area = request.POST.get("area")
        state = request.POST.get("state")
        city = request.POST.get("city")

        if full_name:
            check_full_name = views.name_validator(full_name)
            if check_full_name[0] is True:
                messages.error(request, check_full_name[1])
                return redirect("add_address")
            addresses.full_name = full_name
        if post_office:
            check_post_office = views.validate_post_office_name(post_office)
            if check_post_office[0] is True:
                messages.error(request, check_post_office[1])
                return redirect("add_address")
            addresses.post_office = post_office
        if pincode:
            check_pin = views.validate_pin_code(pincode)
            if check_pin[0] is True:
                messages.error(request, check_pin[1])
                return redirect("add_address")
            addresses.pincode = pincode
        if landmark:
            check_landmark = views.validate_landmark(landmark)
            if check_landmark[0] is True:
                messages.error(request, check_landmark[1])
                return redirect("add_address")
            addresses.landmark = landmark
        if accessible:
            check_accessible = views.validate_area(accessible)
            if check_accessible[0] is True:
                messages.error(request, check_accessible[1])
                return redirect("add_address")
            addresses.accessible = accessible
        if area:
            check_area = views.validate_area(area)
            if check_area[0] is True:
                messages.error(request, check_area[1])
                return redirect("add_address")
            addresses.area = area
        if city:
            check_city = views.validate_city(city)
            if check_city[0] is True:
                messages.error(request, check_city[1])
                return redirect("add_address")
            addresses.city = city
        if state:
            check_state = views.validate_state(state)
            if check_state[0] is True:
                messages.error(request, check_state[1])
                return redirect("add_address")
            addresses.state = state
        if phone:
            check_phone = views.validate_phone(phone)
            if check_phone[0] is True:
                messages.error(request, check_phone[1])
                return redirect("add_address")
            addresses.phone_no = phone
        if alt_phone:
            check_alt_phone = views.validate_phone(alt_phone)
            if check_alt_phone[0] is True:
                messages.error(request, check_alt_phone[1])
                return redirect("add_address")
            addresses.alternative_phone = alt_phone
        if address_type:
            addresses.address_type = address_type

        try:
            addresses.save()
            messages.success(request, "Address updated")
            return redirect("user_profile")
        except Exception as e:
            messages.error(request, f"Error ! {e}")

    return render(request, "user/address_edit.html", context)

#-------------------------------------------- User Deleting Address -------------------------------------------------------#

@login_required
def delete_address(request, address_id):
    storage = messages.get_messages(request)
    storage.used = True

    user_address_to_delete = Address.objects.get(id=address_id)
    user_address_to_delete.delete_address = True
    user_address_to_delete.save()
    messages.success(request, "Address deleted successfully")
    return redirect("user_profile")


#-------------------------------------------- User Changing Password -------------------------------------------------------#

@login_required
def change_password(request):
    storage = messages.get_messages(request)
    storage.used = True

    username = request.user.username
    user_obj = User.objects.get(username=username)
    if request.method == "POST":
        old = request.POST["old_pass"]
        new_password = request.POST["new_pass"]
        password_confirm = request.POST["new_passC"]
        if check_password(old, request.user.password):
            pass_check = views.validate_password(new_password)
            if pass_check[0]:
                messages.error(request, pass_check[1])
                return redirect("change_password")
            if new_password != password_confirm:
                messages.error(request, "Password confirmation failed")
                return redirect("change_password")
            else:
                try:
                    user_obj.set_password(new_password)
                    user_obj.save()
                    messages.success(request, "Password changed successfully")
                    return redirect("user_profile")
                except TypeError:
                    user_object = authenticate(
                        request, username=username, password=new_password
                    )
                    login(request, user_object)
                    messages.success(request, "Password changed successfully")
                    return redirect("user_profile")
        else:
            messages.error(request, "Incorrect password")
            return redirect("change_password")

    return render(request, "user/change_password.html")


#-------------------------------------------- User Adding checkout Address -------------------------------------------------------

@login_required
def add_checkout_address(request):
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == "POST":
        username = request.user.username
        user_data = User.objects.get(username=username)

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        alt_phone = request.POST.get("alt_ph")
        pincode = request.POST.get("pincode")
        post_office = request.POST.get("post_office")
        landmark = request.POST.get("landmark")
        accessible = request.POST.get("accessible")
        address_type = request.POST.get("address_type")
        area = request.POST.get("area")
        state = request.POST.get("state")
        city = request.POST.get("city")

        check_full_name = views.name_validator(full_name)
        check_post_office = views.validate_post_office_name(post_office)
        check_pin = views.validate_pin_code(pincode)
        check_landmark = views.validate_landmark(landmark)
        check_accessible = views.validate_area(accessible)
        check_area = views.validate_area(area)
        check_city = views.validate_city(city)
        check_state = views.validate_state(state)
        check_phone = views.validate_phone(phone)
        check_alt_phone = views.validate_phone(alt_phone)

        if check_full_name[0] is True:
            messages.error(request, check_full_name[1])
            return redirect("add_address")
        if check_post_office[0] is True:
            messages.error(request, check_post_office[1])
            return redirect("add_address")
        if check_pin[0] is True:
            messages.error(request, check_pin[1])
            return redirect("add_address")
        if check_landmark[0] is True:
            messages.error(request, check_landmark[1])
            return redirect("add_address")
        if check_accessible[0] is True:
            messages.error(request, check_accessible[1])
            return redirect("add_address")
        if check_area[0] is True:
            messages.error(request, check_area[1])
            return redirect("add_address")
        if check_city[0] is True:
            messages.error(request, check_city[1])
            return redirect("add_address")
        if check_state[0] is True:
            messages.error(request, check_state[1])
            return redirect("add_address")
        if check_phone[0] is True:
            messages.error(request, check_phone[1])
            return redirect("add_address")
        if check_city[0] is True:
            messages.error(request, check_city[1])
            return redirect("add_address")
        if check_city[0] is True:
            messages.error(request, check_city[1])
            return redirect("add_address")
        if check_alt_phone[0] is True:
            messages.error(request, check_alt_phone[1])
            return redirect("add_address")

        data = UserProfile(
            user=user_data,
            pincode=pincode,
            post_office=post_office,
            landmark=landmark,
            accessible=accessible,
            address_type=address_type,
            area=area,
            state=state,
            city=city,
            alternative_phone=alt_phone,
            phone_no=phone,
            full_name=full_name,
        )
        try:
            data.full_clean()
            data.save()
            messages.success(request, "Address added")
            return redirect("checkout_product")
        except Exception as e:
            messages.error(request, f"Error ! {e}")
    return render(request, "user/address_add.html")


#-------------------------------------------- User Editing Checkout Address -------------------------------------------------------#

@login_required
def edit_checkout_address(request, address_id):
    storage = messages.get_messages(request)
    storage.used = True

    addresses = UserProfile.objects.get(id=address_id)
    context = {
        "user_details": addresses,
    }

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        alt_phone = request.POST.get("alt_ph")
        pincode = request.POST.get("pincode")
        post_office = request.POST.get("post_office")
        landmark = request.POST.get("landmark")
        accessible = request.POST.get("accessible")
        address_type = request.POST.get("address_type")
        area = request.POST.get("area")
        state = request.POST.get("state")
        city = request.POST.get("city")

        if full_name:
            check_full_name = views.name_validator(full_name)
            if check_full_name[0] is True:
                messages.error(request, check_full_name[1])
                return redirect("add_address")
            addresses.full_name = full_name
        if post_office:
            check_post_office = views.validate_post_office_name(post_office)
            if check_post_office[0] is True:
                messages.error(request, check_post_office[1])
                return redirect("add_address")
            addresses.post_office = post_office
        if pincode:
            check_pin = views.validate_pin_code(pincode)
            if check_pin[0] is True:
                messages.error(request, check_pin[1])
                return redirect("add_address")
            addresses.pincode = pincode
        if landmark:
            check_landmark = views.validate_landmark(landmark)
            if check_landmark[0] is True:
                messages.error(request, check_landmark[1])
                return redirect("add_address")
            addresses.landmark = landmark
        if accessible:
            check_accessible = views.validate_area(accessible)
            if check_accessible[0] is True:
                messages.error(request, check_accessible[1])
                return redirect("add_address")
            addresses.accessible = accessible
        if area:
            check_area = views.validate_area(area)
            if check_area[0] is True:
                messages.error(request, check_area[1])
                return redirect("add_address")
            addresses.area = area
        if city:
            check_city = views.validate_city(city)
            if check_city[0] is True:
                messages.error(request, check_city[1])
                return redirect("add_address")
            addresses.city = city
        if state:
            check_state = views.validate_state(state)
            if check_state[0] is True:
                messages.error(request, check_state[1])
                return redirect("add_address")
            addresses.state = state
        if phone:
            check_phone = views.validate_phone(phone)
            if check_phone[0] is True:
                messages.error(request, check_phone[1])
                return redirect("add_address")
            addresses.phone_no = phone
        if alt_phone:
            check_alt_phone = views.validate_phone(alt_phone)
            if check_alt_phone[0] is True:
                messages.error(request, check_alt_phone[1])
                return redirect("add_address")
            addresses.alternative_phone = alt_phone
        if address_type:
            addresses.address_type = address_type

        try:
            addresses.save()
            messages.success(request, "Address updated")
            return redirect("checkout_product")
        except Exception as e:
            messages.error(request, f"Error ! {e}")

    return render(request, "user/address_edit.html", context)


#-------------------------------------------- Admin Handling User Profile -------------------------------------------------------#

def admin_user_profile(request, user_id):
    storage = messages.get_messages(request)
    storage.used = True

    user = User.objects.get(id=user_id)
    addresses = UserProfile.objects.filter(user=user)

    context = {
        "addresses": addresses,
        "user_data": user,
    }
    return render(request, "admin/admin_user_details.html", context)


#-----------------------------------------Finishe User Profile/Address Related Views----------------------------------------------#


