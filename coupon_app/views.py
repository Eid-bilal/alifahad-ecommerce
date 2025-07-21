from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Coupon
from django.db import IntegrityError

#------------------------------ check if user is admin ----------------------------------------------
def is_admin(user):
    return user.is_superuser

#------------------------------ admin coupon list ----------------------------------------------
@user_passes_test(is_admin)
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'admin/coupon_form.html', {'coupons': coupons})
#------------------------------ admin coupon add ----------------------------------------------
@user_passes_test(is_admin)
def coupon_add(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_amount = request.POST.get('discount_amount')
        discount_type = request.POST.get('discount_type')
        min_purchase_amount = request.POST.get('min_purchase_amount')
        usage_limit = request.POST.get('usage_limit')
        valid_until = request.POST.get('valid_until')
        active = request.POST.get('active') == 'on'  


        if Coupon.objects.filter(code=code).exists():
            messages.error(request, f"Coupon with code '{code}' already exists.")
            return render(request, 'admin/coupon_form.html', {'data': request.POST})
        
        try:
            Coupon.objects.create(
                code = code,
                discount_amount = discount_amount,
                discount_type = discount_type,
                min_purchase_amount = min_purchase_amount,
                usage_limit = usage_limit,
                valid_until = valid_until,
                active = active
            )
            messages.success(request, 'Coupon added successfully.')
            return redirect('coupon_list')
        except IntegrityError:
            messages.error(request, f"An error occurred while adding the coupon.")
            return render(request, 'admin/coupon_form.html', {'data': request.POST})
        
    return render(request, 'admin/coupon_form.html')

#------------------------------ admin coupon edit ----------------------------------------------
@user_passes_test(is_admin)
def coupon_edit(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        coupon.code = request.POST.get('code')
        coupon.discount_amount = request.POST.get('discount_amount')
        coupon.discount_type = request.POST.get('discount_type')
        coupon.min_purchase_amount = request.POST.get('min_purchase_amount')
        coupon.usage_limit = request.POST.get('usage_limit')
        coupon.valid_until = request.POST.get('valid_until')
        coupon.active = request.POST.get('active') == 'on'
        coupon.save()
        messages.success(request, 'Coupon updated successfully.')
        return redirect('coupon_list')
    return render(request, 'admin/coupon_edit.html', {'coupon': coupon})

#------------------------------ admin coupon delete ----------------------------------------------
@user_passes_test(is_admin)
def coupon_delete(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully.')
    return redirect('coupon_list')
#------------------------------ admin coupon management ----------------------------------------------




