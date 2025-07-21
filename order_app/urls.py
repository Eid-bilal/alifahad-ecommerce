from django.urls import path
from . import views
from .views import order_detail_view, dashboard_view, view_invoice


app_name = 'order'  # Defining the app namespace

urlpatterns = [

    path("checkout/",views.checkout,name='checkout'),
    path('payment_handler/', views.payment_handler, name='payment_handler'),
    path('retry-payment/', views.retry_payment, name='retry_payment'),
    path('apply-wallet-amount/', views.apply_wallet_amount, name='apply_wallet_amount'),

    # Order success page
    path('order-success/', views.order_success, name='order_success'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('invoice/<int:order_id>/', view_invoice, name='view_invoice'), # generating invoice for celery----
    path('all-orders/', views.all_orders, name='all_orders'),
    path('order/<int:serial_number>/', views.order_detail, name='order_detail'),
    path('order/cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),

    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('request_item_return/<int:item_id>/', views.request_item_return, name='request_item_return'),
    path('add_checkout_address/', views.add_checkout_address, name='add_checkout_address'),
    path('edit_checkout_address/<int:address_id>/', views.edit_checkout_address, name='edit_checkout_address'),
    

    path('order-management/', views.order_management, name='order_management'),
    path('admin-order/<int:order_serial_number>/', order_detail_view, name='order_detail_view'),
    path('change_order_status/<int:serial_number>/', views.change_order_status, name='change_order_status'),
    path('change_order_item_status/<oid>/', views.change_order_item_status, name='change_order_item_status'),
    path('approve_item_return/<int:item_id>/', views.approve_item_return, name='approve_item_return'),

    path('dashboard/', dashboard_view, name='dashboard'),
    path('order-analytics/', views.get_order_analytics, name='order-analytics'),
    path('get_top_selling_categories/', views.get_top_selling_categories, name='get_top_selling_categories'),
    path('generate-pdf/', views.generate_pdf_report, name='generate_pdf_report'),
    path('generate-excel/', views.generate_excel_report, name='generate_excel_report'),

    path('top_categories/', views.top_categories, name='top_categories'),
    path('top_products/', views.top_products, name='top_products'),
    path('top_customers/', views.top_customers, name='top_customers'),
    path('top_pincodes/', views.top_pincodes, name='top_pincodes'),

    



]
