from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('product/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('orderlist/', views.OrderListView.as_view(), name='orderlist'),  #staff view: all order
    path('order/<uuid:uuid>', views.OrderDetailView.as_view(), name='order_detail'),
]
urlpatterns += [
    path('neworder/', views.neworder, name='neworder'),
    path('checkorder/', views.checkorder, name='checkorder'),
    path('order_result/', views.order_result, name='order_result'),
]
urlpatterns += [
    path('order/<uuid:uuid>/update', views.update_orderview_staff, name='updateorder_staff'),
    path('order/<uuid:uuid>/delete', views.delete_orderview_staff, name='deleteorder_staff'),
]
urlpatterns += [
    path('order/<uuid:uuid>/update/customer', views.update_orderview_customer, name='updateorder_customer'),
]