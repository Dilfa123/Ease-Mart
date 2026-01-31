from django.db import models
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
class CategoryModel(models.Model):
    name=models.CharField(max_length=100,unique=True)
    is_delete=models.BooleanField(default=False)
    def __str__(self):
        return self.name
# Create your models here.
class Products(models.Model):
    title=models.CharField(max_length=100)
    discription=models.TextField(null=True)
    price=models.IntegerField(default=0)
    image=models.ImageField(upload_to='images/')
    category=models.ForeignKey(CategoryModel,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    quantity=models.PositiveIntegerField(default=0)
    is_delete=models.BooleanField(default=False)
    def __str__(self):
        return self.title
class Images(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='images/')
    def __str__(self):
        return self.product.title
class Coupons(models.Model):
    code=models.CharField(max_length=6,unique=True)
    discount=models.PositiveIntegerField(help_text='flat_discount')
    is_active=models.BooleanField(default=True)
    created_on=models.DateTimeField(auto_now_add=True)
    start_date=models.DateField(null=True)
    expire_date=models.DateField()
    min_purchase=models.PositiveIntegerField(default=0)
    
    @property
    def is_expired(self):
        return self.expire_date < timezone.now().date()

    @property
    def is_started(self):
        if self.start_date is None:
            return False
        return self.start_date <= timezone.now().date()


    def clean(self):
   
        if self.start_date and self.expire_date:
            if self.start_date > self.expire_date:
             raise ValidationError(
                "Start date cannot be after expiry date"
            )

    
        if self.min_purchase is not None and self.discount is not None:
            if self.min_purchase < self.discount:
                raise ValidationError(
                 'Discount must be less than minimum purchase'
            )


    def save(self, *args, **kwargs):
        self.full_clean()   
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code