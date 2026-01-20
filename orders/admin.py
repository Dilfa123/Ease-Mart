from django.contrib import admin
from .models import WalletTransaction,AdminWallet
# Register your models here.
from .models  import Order_item,Order
admin.site.register(Order)
admin.site.register(WalletTransaction)
admin.site.register(AdminWallet)
