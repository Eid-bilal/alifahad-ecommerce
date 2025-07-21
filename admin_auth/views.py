from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.

#-------------------- Admin login ------------------------------------------------------------------------------------

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel') 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:  
            login(request, user)
            return redirect('panel')  
        else:
            return render(request, 'admin/admin_login.html', {'error': 'Invalid credentials or access denied'})
    return render(request, 'admin/admin_login.html')

#------------ Admin panel ------------------------------------------------------------------------------------------------------

def panel(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')
    
    return render(request, 'admin/dashboard.html')

#------------ User management -----------------------------------------------------------------------------------------------------


def user_managment(request): 
    if not request.user.is_authenticated or not request.user.is_superuser:  
        return redirect('admin_login') 
   


    query = request.GET.get('q', '').strip()  # Default to an empty string if no query provided

    # Default queryset to all users
    my_users = User.objects.filter(is_superuser =  False).order_by('username')

    # If there is a query, filter the users
    if query:
        my_users = my_users.filter(
            Q(username__icontains=query) |           
            Q(phone__mobile__icontains=query) |      
            Q(email__icontains=query)               
        )


    paginator = Paginator(my_users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request,'admin/users.html',{'users':users, 'query': query})

#------------- Block and unblock user ----------------------------------------------------------------------------------------------

def block_unblock_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:  
        return redirect('admin_login') 

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'block':
            user.is_active = False
        elif action == 'unblock':
            user.is_active = True
        user.save()

    return redirect('user_management')  


#------------- Admin logout -------------------------------------------------------------------------------------------------

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

#-----------------------------------------------------------------------------------------------------------------------------