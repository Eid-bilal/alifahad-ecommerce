from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from .models import Category
from .forms import CategoryForm
from django.contrib import messages
import re
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import CharField

#--------------------- Admin Category management --------------------------------------------------------------------------------
def category_management(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login') 
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect(reverse('category_management'))
        else:
           
            errors = form.errors

    else:
        errors = None

    

    query = request.GET.get('q', '').strip()

    categories = Category.objects.annotate(
        created_at_str=Cast('created_at', CharField())  # Cast created_at to CharField
    )

    if query:
        categories = categories.filter(
            Q(category_name__icontains=query) |
            Q(category_unit__icontains=query) |
            Q(created_at_str__icontains=query)
        )

    
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)

    return render(request, 'admin/category.html', {
        'categories': categories,
        'form': form,
        'errors': errors,
        'query': query
    })

#------------------- Admin Edit category -----------------------------------------------------------------------------------------------

def edit_category(request, category_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login') 
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')
        category_offer = request.POST.get('category_offer')
        category_unit = request.POST.get('category_unit')

        errors = []

       
        if Category.objects.exclude(id=category_id).filter(category_name__iexact=category_name).exists():
            errors.append('Category name already exists')


        if not re.match("^[A-Za-z\s]+$", category_name):
            errors.append('Category name must contain letters and spaces only')
            print(errors)

        if errors:
            return render(request, 'admin/edit_category.html', {
                'category': category,
                'errors': errors,
                'categories': Category.objects.all(),
                'units': Category.objects.values_list('category_unit', flat=True).distinct()
            })

        
        category_name = category_name.title()  
     

       
        category.category_name = category_name
        category.category_image = category_image
        category.category_offer = category_offer
        category.category_unit = category_unit
        category.save()

        messages.success(request, 'Category updated successfully.')
        
        return redirect('category_management')

    return render(request, 'admin/edit_category.html', {
        'category': category,
        'categories':Category.objects.all(),
        'units': Category.objects.values_list('category_unit', flat=True).distinct()
    })


#------------------ category list and unlist ---------------------------------------------------------------------------------------------

def toggle_category_listing(request, category_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login') 
    category=  get_object_or_404(Category,id = category_id)
    category.is_listed = not category.is_listed
    category.save()
    return redirect('category_management')

#--------------------------------------------------------------------------------------------------------------------------------------------