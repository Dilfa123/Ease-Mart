from django.urls import path
from . import views

urlpatterns=[
    path('',views.homeview,name='home'),
    path('category/<int:pk>/',views.category_page,name='category'),
    path('error_page',views.error_page,name='error_page'),
    path('add_product',views.add_product,name='add_product'),
    path('delete_product/<int:pk>/',views.delete_product,name='delete_product'),
    path('product_detail/<int:pk>/',views.product_detail,name='product_detail'),
    path('add_category',views.add_category,name='add_category'),
    path('edit_category/<int:pk>/',views.edit_category,name='edit_category'),
    path('delete_category<int:pk>/',views.delete_category,name='delete_category'),
    path('edit_product/<int:pk>/',views.edit_product,name='edit_product'),
    path('user_single_product/<int:pk>/',views.user_single_product,name='user_single_product'),
    

]



