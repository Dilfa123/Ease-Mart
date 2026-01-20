from django.urls import path
from . import views

urlpatterns=[
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('cart_products',views.cart_products,name='cart_products'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('checkout',views.checkout,name='checkout'),
    path('increase_quantity/<int:pk>/',views.increase_quantity,name='increase_quantity'),
    path('decrease_quantity/<int:pk>/',views.decrease_quantity,name='decrease_quantity'),
    path('add_coupon',views.add_coupon,name='add_coupon'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),

]