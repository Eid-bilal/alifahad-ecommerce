
#---------------------------- cart item count -------------------------------------------------------------------

from .models import CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        # Retrieve the total count of all items in the user's cart
        cart_items = CartItem.objects.filter(cart__user_id=request.user)
        count = sum(item.quantity for item in cart_items)
        # count = CartItem.objects.filter(cart__user_id=request.user).count()
    else:
        count = 0  # For unauthenticated users, default to 0
    return {'cart_item_count': count}
