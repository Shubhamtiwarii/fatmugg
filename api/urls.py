# urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Vendor Profile Management
    path('api/vendors/', views.vendor_list, name='vendor-list'),
    path('api/vendors/<int:vendor_id>/', views.vendor_detail, name='vendor-detail'),

    # Purchase Order Tracking
    path('api/purchase_orders/', views.purchase_order_list, name='purchase-order-list'),
    path('api/purchase_orders/<int:po_id>/', views.purchase_order_detail, name='purchase-order-detail'),

    # Vendor Performance Evaluation
    path('api/vendors/<int:vendor_id>/performance/', views.vendor_performance, name='vendor-performance'),
    
    path('api/purchase_orders/<int:po_id>/acknowledge/', views.acknowledge_purchase_order, name='acknowledge-purchase-order'),

]
