from django.utils import timezone
from django.shortcuts import render,get_object_or_404,redirect
from products.models import Products,Coupons
from .models import Cart,Cart_items
from users.models import Address
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from users.models import UserWallet
# Create your views here.
def get_create_cart(user):
    cart,created=Cart.objects.get_or_create(user=user)
    return cart
    
@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Products, pk=pk)
    cart = get_create_cart(request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        messages.error(request, "Invalid quantity")
    if qty > product.quantity:
        messages.error(request, "Requested quantity not available")
    
    item, created = Cart_items.objects.get_or_create(
        cart=cart,
        product=product
    )

    new_qty = item.quantity + qty

    if new_qty > product.quantity:
        messages.error(request, "Not enough stock available")
       

    item.quantity = new_qty
    item.save()
   
    messages.success(request, "Product added to cart")
    return redirect('cart_products')

def increase_quantity(request,pk):
    item=get_object_or_404(Cart_items,pk=pk,cart__user=request.user)
    product=item.product
    if item.quantity < product.quantity:
        item.quantity+=1
        item.save()
    else:
        messages.error(request, "No more stock available")
    return redirect('cart_products')
def decrease_quantity(request,pk):
     item=get_object_or_404(Cart_items,pk=pk,cart__user=request.user)
     product=item.product
    
     if item.quantity > 1:
        item.quantity -= 1
        item.save()
     return redirect('cart_products')
        


def cart_products(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cart=get_create_cart(request.user)
    items=Cart_items.objects.filter(cart=cart)
    total=0
    for item in items:
        total+=item.product.price * item.quantity
    return render(request,'cart/cart_products.html',{'items':items,'total':total})
    

def remove_from_cart(request,pk):
    item=get_object_or_404(Cart_items,pk=pk)
    item.delete()
    return redirect('cart_products')

@login_required(login_url='login')
def checkout(request):
    user = request.user
    address = Address.objects.filter(user=user)
    default_address = Address.objects.filter(
    user=user,
    is_default=True
).first()
    coupons=Coupons.objects.filter(is_active=True)
    wallet, _ = UserWallet.objects.get_or_create(user=user)
    from_cart = request.GET.get('cart')
    items = []
    subtotal = 0
    
      
    if from_cart:
        cart, created= Cart.objects.get_or_create(user=user)
        items = Cart_items.objects.filter(cart=cart)
        for item in items:
            if item.product.quantity < item.quantity:
               messages.error( request, f"{item.product.title} is out of stock or insufficient quantity")
               return redirect('cart_products')
          
        if not items.exists():
            return redirect('cart_products')

       
        subtotal += sum(item.product.price * item.quantity for item in items)

    discount = validate_and_apply_coupon(request, subtotal)
    total=max(subtotal-discount,0)
    error = None
   

    # if request.method == 'POST':
    #     coupon_code = request.POST.get('coupon')
    #     if coupon_code:
    #         try:
    #             coupon = Coupons.objects.get(code__iexact=coupon_code, is_active=True)
    #             discount = coupon.discount
    #         except Coupons.DoesNotExist:
    #             error = "Invalid coupon code"
    # total = max(subtotal - discount, 0)
    return render(request, 'cart/checkout.html', {
        'items': items,
        'address': address,
        'default_address':default_address,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'error': error,
        'wallet':wallet
       
    })
def validate_and_apply_coupon(request, subtotal, coupon=None):
    """
    Returns discount amount if valid, else removes coupon from session.
    """
    try:
        if not coupon:
            code = request.session.get('coupon_code')
            if not code:
                return 0
            coupon = Coupons.objects.get(code=code, is_active=True)

       
        if coupon.is_expired:
            raise Exception("Expired")

        
        if subtotal < coupon.min_purchase:
            raise Exception("Min purchase not met")

        
        if coupon.discount >= subtotal / 2:
            raise Exception("Invalid discount")
       
       
        request.session['coupon_code'] = coupon.code
        request.session['coupon_discount'] = coupon.discount
        return coupon.discount

    except Exception:
        
        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        return 0

@login_required
def add_coupon(request):
    user = request.user
    cart = get_create_cart(user)
    items = Cart_items.objects.filter(cart=cart)

    today = timezone.now().date()

   
    coupons = Coupons.objects.filter(
        is_active=True,
        start_date__lte=today,
        expire_date__gte=today
    )

    subtotal = sum(item.product.price * item.quantity for item in items)
    discount = 0

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')

        if coupon_code:
            try:
                coupon = Coupons.objects.get(
                    code__iexact=coupon_code,
                    is_active=True,
                    expire_date__gte=today,
                    start_date__lte=today,
                )

                
                if subtotal < coupon.min_purchase:
                    messages.error(
                        request,
                        f"Minimum purchase ₹{coupon.min_purchase} required"
                    )
                else:
                    discount = coupon.discount
                    request.session['coupon_code'] = coupon.code
                    request.session['coupon_discount'] = discount
                    messages.success(request, "Coupon applied successfully")
                    return redirect(reverse('checkout') + '?cart=1')

            except Coupons.DoesNotExist:
                messages.error(request, "Invalid or expired coupon")

    total = max(subtotal - discount, 0)

    return render(request, 'orders/add_coupon.html', {
        'total': total,
        'subtotal': subtotal,
        'coupons': coupons,
    })

def remove_coupon(request):
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    url=reverse('checkout')+ '?cart=1'
    return redirect(url)
        