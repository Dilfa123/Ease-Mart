from django.contrib import admin
from .models import User,Admin_model,Otp,Address,UserWallet
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=[
        'id','username','email'
    ]
admin.site.register(User,UserAdmin)
admin.site.register(Admin_model)
admin.site.register(Otp)
admin.site.register(Address)
admin.site.register(UserWallet)
