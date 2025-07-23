from django.shortcuts import render,redirect,get_object_or_404
from . models import Product, Variant
from category_app.models import Category
from django.contrib.auth.models import User
from . forms import ProductForm
from django.db.models import  F, Count
from django.contrib import messages
from django.db import models
from django.db.models import Avg
import re
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Variant
from review_app.models import Rating, Review
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import CharField
# Create your views here.


#=============== Product list =======================================================================================================
def product_list(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')  
    if request.method == 'POST':
        print("yes i am insdie product list view ")
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print("adedd the product")
            form.save()
            messages.success(request, 'Product added successfully!')
            print("saved ok ")
            return redirect('product_management')  # Adjust as necessary
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print("error ind ")
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = ProductForm()
        errors = None

    products_list = Product.objects.all()
    # print("ethokeyan product list",product_list)
    query = request.GET.get('q', '').strip()
    
    if query:
        products_list = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(category__category_name__icontains=query) 
        )

    # products_list = Product.objects.all().order_by('available_stock')
    paginator = Paginator(products_list, 8)  # Show 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    categories = Category.objects.all()
    
    return render(request, 'admin/product.html', {
        'form': form,
        'product': products,
        'categories': categories,
        'errors': errors,
        'query': query
    })

#================ Edit product ========================================================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Variant, VariantSize
from .forms import ProductForm

def edit_product(request, product_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    product = get_object_or_404(Product, id=product_id)
    variants = Variant.objects.filter(product=product)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/edit_product.html', {
        'form': form,
        'product': product,
        'categories': Category.objects.all(),
        'variants': variants,
        'unit_choices': VariantSize.UNIT_CHOICES,
    })
#==================== Product list and unlist ========================================================================================
  
def toggle_product_listing(request, product_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login') 
    
    product = get_object_or_404(Product, id=product_id)
    product.is_listed = not product.is_listed
    product.save()
    return redirect('product_management')

#============= to ge size choices ====================================================================================================
# product_app/views.py
from django.shortcuts import render
from django.db.models import Q
from category_app.models import Category
from variant_size_app.models import VariantSize
from .models import Product, Variant

def get_size_choices(category_name):
    try:
        # Get the Category object
        category = Category.objects.get(category_name__iexact=category_name)
        # Query VariantSize objects for the category
        sizes = VariantSize.objects.filter(category=category)
        # Return size choices as [(value, label), ...]
        return [(size.size_name, size.size_name) for size in sizes]
    except Category.DoesNotExist:
        return []
#============= variant list ====================================================================================================
def variant_list(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        variants = Variant.objects.filter(product_id=product_id)
        size_choices = get_size_choices(product.category.category_name)
        return render(request, 'admin/variant_list.html', {
            'product': product,
            'variants': variants,
            'size_choices': size_choices,
            'unit_choices': VariantSize.UNIT_CHOICES,
        })
    except Product.DoesNotExist:
        return render(request, 'admin/variant_list.html', {'error': 'Product not found'})
#============= add variants ====================================================================================================
# product_app/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import VariantSize, Product, Variant

def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        size_name = request.POST.get('size_name')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        # Validate unit is in UNIT_CHOICES
        if unit not in dict(VariantSize.UNIT_CHOICES).keys():
            messages.error(request, 'Invalid unit selected.')
            return redirect('edit_product', product_id=product.id)
        
        # Get or create VariantSize
        variant_size, created = VariantSize.objects.get_or_create(
            size_name=size_name,
            unit=unit,
            category=product.category,  # Assumes product has a category
        )
        
        # Create Variant
        Variant.objects.create(
            product=product,
            size=variant_size,
            price=price,
            stock=stock
        )
        messages.success(request, 'Variant added successfully!')
        return redirect('edit_product', product_id=product.id)
    return redirect('edit_product', product_id=product.id)

#============= update variant ====================================================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import VariantSize, Product, Variant

def update_variant(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    size_choices = get_size_choices(variant.product.category.category_name.lower())
    
    if request.method == "POST":
        size_name = request.POST.get("size", "").strip()
        price = request.POST.get("price", "").strip()
        stock = request.POST.get("stock", "").strip()
        unit = request.POST.get("unit", "").strip()  # Assuming unit is passed in the form

        # Validate inputs
        if not size_name or not price or not stock or not unit:
            messages.error(request, "All fields are required.")
            return redirect('update_variant', variant_id=variant_id)
        
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messages.error(request, "Price and stock must be valid numbers.")
            return redirect('update_variant', variant_id=variant_id)

        if price < 0:
            messages.error(request, 'Price must be a positive number.')
            return redirect('update_variant', variant_id=variant_id)
        
        if stock < 0:
            messages.error(request, 'Stock must be a positive number.')
            return redirect('update_variant', variant_id=variant_id)

        # Validate unit
        if unit not in dict(VariantSize.UNIT_CHOICES).keys():
            messages.error(request, 'Invalid unit selected.')
            return redirect('update_variant', variant_id=variant_id)

        # Get or create VariantSize instance
        try:
            variant_size = VariantSize.objects.get(
                size_name=size_name,
                unit=unit,
                category=variant.product.category
            )
        except VariantSize.DoesNotExist:
            variant_size = VariantSize.objects.create(
                size_name=size_name,
                unit=unit,
                category=variant.product.category
            )

        # Update variant
        variant.size = variant_size  # Assign VariantSize instance
        variant.price = price
        variant.stock = stock
        variant.save()
        messages.success(request, "Variant updated successfully.")
        return redirect('admin/variant_list.html', product_id=variant.product.id)

    return render(request, 'admin/variant_update.html', {'variant': variant, 'size_choices': size_choices})


#============ User side products ====================================================================================================

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Min
from .models import Product, Variant
from category_app.models import Category

def user_products(request):
    username = request.user.username if request.user.is_authenticated else None
    category = request.GET.get('category', 'All')
    sort_by = request.GET.get('sort', '')  # Changed from 'sort_by' to match template
    search_query = request.GET.get('q', '').strip()  # Changed from 'search' to match template
    page_number = request.GET.get('page', 1)

    # Base queryset: only listed products
    product_list = Product.objects.filter(is_listed=True)

    # Apply category filter
    if category != 'All':
        product_list = product_list.filter(category__category_name__iexact=category)

    # Apply search query
    if search_query:
        product_list = product_list.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )

    # Apply sorting
    if sort_by == 'price_low_high':
        # Annotate with minimum variant price
        product_list = product_list.annotate(
            min_price=Min('variants__price')
        ).order_by('min_price')
    elif sort_by == 'price_high_low':
        product_list = product_list.annotate(
            min_price=Min('variants__price')
        ).order_by('-min_price')
    elif sort_by == 'discount':
        product_list = product_list.annotate(
            max_discount=Min('variants__offer_percentage')
        ).order_by('-max_discount')
    elif sort_by == 'new_arrivals':
        product_list = product_list.order_by('-created_at')
    elif sort_by == 'a_to_z':
        product_list = product_list.order_by('product_name')
    elif sort_by == 'z_to_a':
        product_list = product_list.order_by('-product_name')

    # Pagination
    paginator = Paginator(product_list, 8)  # Increased to 8 products per page
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Get all categories for the filter dropdown/buttons
    categories = Category.objects.filter(is_listed=True)

    return render(request, 'user/shop.html', {
        'products': products,
        'username': username,
        'categories': categories,
        'selected_category': category,
        'selected_sort': sort_by,
        'query': search_query,
    })
def get_size_choices(category_name):
    return {
        'units': VariantSize.UNIT_CHOICES,
        'sizes': VariantSize.objects.filter(category__category_name__iexact=category_name).values('size_name', 'unit')
    }
#============== Product details ======================================================================================================
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_listed=True)
    variants = product.variants.all()
    reviews = Review.objects.filter(product=product)

    average_rating = reviews.aggregate(average=Avg('score'))['average'] or 0

    total_reviews = reviews.count()

    # Calculate the rating distribution (the count of each rating 1, 2, 3, 4, 5)
    rating_distribution = reviews.values('score').annotate(count=Count('score')).order_by('-score')

    rating_percentage = {}
    for rating in range(1, 6):
        count = next((item['count'] for item in rating_distribution if item['score'] == rating), 0)
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_percentage[rating] = percentage

    # Set the highest offer for each variant
    for variant in variants:
        variant.highest_offer = max(
            variant.offer_percentage,
            variant.product.offer_percentage,
            variant.product.category.category_offer
        )

    # Prepare the context to pass to the template
    context = {
        'product': product,
        'variants': variants,
        'offer': variant.highest_offer,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'rating_count': total_reviews,
        'rating_percentage': rating_percentage,
    }
    
    # Render the template with the context data
    return render(request, 'user/product-detail.html', context)
#=======================================================================================================================================