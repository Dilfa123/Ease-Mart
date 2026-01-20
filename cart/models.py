from django.db import models
from django.conf import settings
from products.models import Products

# Create your models here.
class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}'s cart"
    
class Cart_items(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title}"
    @property
    def item_total(self):
        return self.product.price * self.quantity
    

