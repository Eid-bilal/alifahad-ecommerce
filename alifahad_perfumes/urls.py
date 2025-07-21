"""
URL configuration for alifahad_perfumes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user_auth import views

urlpatterns = [
    path('builtin_admin/', admin.site.urls),
    path('admin/', include('admin_auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('category/', include('category_app.urls')),
    path('product/', include('product_app.urls')),
    path('user/', include('user_auth.urls')),
    path('profile/', include('user_profile_app.urls')),
    path('cart/', include('cart_app.urls')),
    path('order/', include('order_app.urls')),
    path('coupon/', include('coupon_app.urls')),
    path('wishlist/', include('wishlist_app.urls')),
    path('wallet/', include('wallet_app.urls')),
    path('review/', include('review_app.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('', views.redirect_to_home), 
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

