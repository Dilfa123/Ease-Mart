from django.urls import path
from .views import stripe_webhook
from . import views
from .views import stripe_webhook

# app_name = "orders"
urlpatterns=[
    path('pay_order/',views.pay_order,name='pay_order'),
    path('success_page/',views.success_page,name='success_page'),
    path('order_items/',views.order_items,name='order_items'),
    # path('stripe_webhook/',views.stripe_webhook,name='stripe_webhook'),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path("order_cancel/<int:order_id>/",views.order_cancel,name='order_cancel'),
    path('wallet_view/',views.wallet_view,name='wallet_view'),
    path('wallet_pay_order/',views.wallet_pay_order,name='wallet_pay_order')
    
   

]   