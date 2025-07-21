from django.urls import path
from . import views




urlpatterns = [
    path('home/', views.user_home, name='home'),
    path('signup/', views.user_registration, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<str:email>/', views.resend_otp, name='resend_otp'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('shop/', views.shop, name='shop'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),
    path('reset_new_password/', views.reset_new_password, name='reset_new_password'),
    path('reset_resend_otp/', views.reset_resend_otp, name='reset_resend_otp'),
    
    

]
