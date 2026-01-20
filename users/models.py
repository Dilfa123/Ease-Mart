from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    def __str__(self):
        return self.username
    


class Otp(models.Model):
    otp=models.CharField(max_length=6)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.otp
    
    
class Password(models.Model):
    newpass=models.CharField(max_length=100)
    cnfrm_pass=models.CharField(max_length=100)

class Pass_Otp(models.Model):
    otp=models.CharField(max_length=4)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_on=models.DateTimeField(auto_now_add=True)

class Admin_model(models.Model):
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    def __str__(self):
        return self.username
class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    place=models.TextField(null=True)
    phone=models.CharField(max_length=10)
    pincode=models.CharField(max_length=6)
    is_default=models.BooleanField(default=False)
    def __str__(self):
        return  f"{self.user.username} - {self.place} ({self.pincode})"
    def save(self,*args,**kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True, ).exclude(pk=self.pk).update(is_default=False)
            
        super().save(*args, **kwargs)
class OrderAddress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    place=models.TextField(null=True)
    phone=models.CharField(max_length=10)
    pincode=models.CharField(max_length=6)
    def __str__(self):
        return f"{self.place} - {self.pincode}"
class UserWallet(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    balance=models.DecimalField(decimal_places=2,max_digits=10,default=0)
    def __str__(self):
        return f"{self.user} - ₹{self.balance}"
class UserTransactions(models.Model):
    TRANSACTION_TYPE=(
        ('CREDIT','credit'),
        ('DEBIT','debit'),
    )
    wallet=models.ForeignKey(UserWallet,on_delete=models.CASCADE)
    amount=models.DecimalField(decimal_places=2,max_digits=10)
    transaction_type=models.CharField(choices=TRANSACTION_TYPE,max_length=10)
    created_at=models.DateTimeField(auto_now_add=True)
    description=models.CharField(max_length=200,blank=True)
