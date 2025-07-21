from django.urls import path
from . import views

urlpatterns = [
    path("wallet/", views.user_wallet, name="user-wallet"),
    path('spin/', views.spin_wheel, name='spin_wheel'),
    path('transactions/', views.transaction_history, name='transaction_history'),
]
