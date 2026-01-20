from django.contrib import admin
from .models import Products,CategoryModel,Images,Coupons
# Register your models here.
admin.site.register(Products)
admin.site.register(CategoryModel)
admin.site.register(Images)
admin.site.register(Coupons)