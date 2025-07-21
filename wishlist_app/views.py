from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from cart_app.models import Wishlist, Cart, CartItem
from product_app.models import Variant, Product
from cart_app.views import update_cart_total
from django.contrib import messages
import json

# Create your views here.

#--------------------------------- Add to wishlist --------------------------------------------------------
@login_required
def add_to_wishlist(request):
    if request.method == 'POST':  # Ensure POST method
        try:
            data = json.loads(request.body)
            variant_id = data.get('variant_id')

            if not variant_id:
                return JsonResponse({'status': 'error', 'message': 'Variant ID is required.'}, status=400)

            variant = get_object_or_404(Variant, id=variant_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user, variant=variant)

            if created:
                response = {
                    'status': 'success',
                    'message': f"{variant.product.product_name} ({variant.size}) has been added to your wishlist.",
                }
            else:
                response = {
                    'status': 'info',
                    'message': f"{variant.product.product_name} ({variant.size}) is already in your wishlist.",
                }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


#--------------------------------- Remove from wishlist --------------------------------------------------------

@login_required
def remove_from_wishlist(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, variant=variant).first()

    if wishlist_item:
        wishlist_item.delete()
        response = {
            'status': 'success',
            'message': f"{variant.product.product_name} ({variant.size}) has been removed from your wishlist.",
        }
    else:
        response = {
            'status': 'error',
            'message': "This variant was not in your wishlist.",
        }

    return JsonResponse(response)

#--------------------------------- View wishlist --------------------------------------------------------

@login_required
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('variant__product')
    
    return render(request, 'user/wishlist.html', {'wishlist_items': wishlist_items})

#--------------- wishlisted item add to cart --------------------------------------------------------------


@login_required
def move_to_cart(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, variant=variant)

    
    quantity = 1
    if quantity > variant.stock:
        messages.error(request, "Requested quantity exceeds available stock.")
        return redirect('wishlist')

    
    cart, created = Cart.objects.get_or_create(user_id=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

    
    total_quantity = cart_item.quantity + quantity if not created else quantity
    
    if total_quantity > 5:
        messages.error(
            request,
            f"You cannot add more than 5 of this item to your cart. "
            f"Current quantity in cart: {cart_item.quantity}."
        )
        return redirect('wishlist')

    
    cart_item.quantity = total_quantity
    cart_item.save()

    
    cart_item.sub_total = cart_item.quantity * variant.product_price_after()
    cart_item.save()
    update_cart_total(cart)

    
    wishlist_item.delete()
    messages.success(request, "Product variant moved from wishlist to cart.")
    return redirect('wishlist')

#--------------------------------------------------------------------------------------------------------------------------
