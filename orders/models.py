from django.db import models
from users.models import User
from products.models import Products
from users.models import Address,OrderAddress
# Create your models here.
class Order(models.Model):
    STATUS_CHOICES=(
        ('placed','Placed'),
        ('confirmed','Confirmed'),
        ('packed','Packed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('cancelled','cancelled')
    )
    
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address=models.ForeignKey(OrderAddress,on_delete=models.PROTECT,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    total_amount=models.PositiveIntegerField()
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='placed')
    refund_to_wallet=models.BooleanField(default=False)
    is_paid=models.BooleanField(default=False)
    stripe_session_id=models.CharField(max_length=255,blank=True,null=True)
    payment_method=models.CharField(max_length=50,choices=(('stripe','stripe'),('wallet','wallet')),default='stripe')
    def __str__(self):
        return f"order :{self.id}"

class Order_item(models.Model):
    order=models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    price=models.PositiveIntegerField()

class AdminWallet(models.Model):
    balance=models.DecimalField(max_digits=20,decimal_places=2,default=0)
class WalletTransaction(models.Model):
    wallet=models.ForeignKey(AdminWallet,on_delete=models.CASCADE)
    order=models.ForeignKey(Order,related_name='order',on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)