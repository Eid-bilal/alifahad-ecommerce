from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, CartItem, Variant
from django.contrib import messages
from django.views.decorators.cache import never_cache

#-------------------------- add to cart ----------------------------------------------------
@login_required(login_url='login')
def add_to_cart(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))  # Quantity being added now
        variant = get_object_or_404(Variant, id=variant_id)

        # Check stock availability
        if quantity > variant.stock:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect('product_details', product_id=variant.product.id)

        # Fetch or create cart and cart item
        cart, created = Cart.objects.get_or_create(user_id=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

        # Calculate the total quantity if added
        total_quantity = cart_item.quantity + quantity if not created else quantity

        # Validate against the 5-item limit
        if total_quantity > 5:
            messages.error(
                request,
                f"You cannot add more than 5 of this item to your cart. "
                f"Current quantity in cart: {cart_item.quantity}."
            )
            return redirect('product_details', product_id=variant.product.id)

        # Update cart item quantity and save
        cart_item.quantity = total_quantity
        cart_item.save()

        # Calculate subtotal and update cart totals
        cart_item.sub_total = cart_item.quantity * variant.product_price_after()
        cart_item.save()
        update_cart_total(cart)

        messages.success(request, "Item added to cart successfully!")
        return redirect('product_details', product_id=variant.product.id)

    return redirect('home') 

#-------------------------- cart show ----------------------------------------------------
@login_required(login_url='login')
def cart_show(request):
    storage = messages.get_messages(request)
    storage.used = True
    try:
        cart = Cart.objects.filter(user_id=request.user).first()
        cart_items = cart.items.filter(variant__product__is_listed=True) if cart else []
        shipping = 150 if cart and cart.total_amount_without_coupon < 1000 else 0

        return render(request, 'user/cart_show.html', {
            'cart': cart,
            'cart_items': cart_items,
            'shipping': shipping,
        })
    except Exception as e:
        return render(request, 'user/cart_show.html', {'error': str(e)})

#-------------------------- update cart total ----------------------------------------------------

def update_cart_total(cart):
    try:
        items = cart.items.all()  # Get all cart items
        subtotal = sum(item.sub_total for item in items)
        shipping = 150 if subtotal < 1000 else 0
        grand_total = subtotal + shipping

        # Update the cart model fields
        cart.total_amount_without_coupon = subtotal
        cart.total_amount = grand_total
        cart.save()

    except Exception as e:
        print(f"Error updating cart total: {e}")

#-------------------------- update cart item quantity ----------------------------------------------------


def update_cart_item_quantity(request):
    storage = messages.get_messages(request)
    storage.used = True
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')  # 'increment' or 'decrement'

        if action not in ['increment', 'decrement']:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user_id=request.user)

            if action == 'increment':
                if cart_item.quantity < 5:
                    cart_item.quantity += 1
                else:
                    # return JsonResponse({'error': 'Maximum quantity of 5 reached'}, status=400)
                    messages.error(request, "Maximum quantity of 5 reached!")
            elif action == 'decrement':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    # return JsonResponse({'error': 'Minimum quantity is 1'}, status=400)
                    messages.error(request, "Minimum quantity is 1")

            # Ensure stock availability
            if cart_item.quantity > cart_item.variant.stock:
                return JsonResponse({'error': 'Not enough stock available'}, status=400)

            cart_item.sub_total = cart_item.quantity * cart_item.variant.product_price_after()
            cart_item.save()

            # Update cart total
            update_cart_total(cart_item.cart)

            return JsonResponse({
                'quantity': cart_item.quantity,
                'sub_total': cart_item.sub_total,
                'total_amount': cart_item.cart.total_amount,
                'shipping': 150 if cart_item.cart.total_amount_without_coupon < 1000 else 0,
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

#-------------------------- remove cart item ----------------------------------------------------

def remove_cart_item(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')

        try:
            # Fetch the cart item
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user_id=request.user)

            # Remove the item from the cart
            cart_item.delete()

            # Update the cart total after removing the item
            update_cart_total(cart_item.cart)

            return JsonResponse({
                'message': 'Item removed from cart',
                'total_amount': cart_item.cart.total_amount,
                'shipping': 150 if cart_item.cart.total_amount_without_coupon < 1000 else 0,
            }, status=200)

        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


#----------------------------------------------------------------------------------------------------------------------
