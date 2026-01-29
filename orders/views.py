
from django.shortcuts import get_object_or_404, render
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from cart.models import Cart,Cart_items
from cart.views import get_create_cart
from .models import Order,Order_item,AdminWallet,WalletTransaction
from users.models import Address,OrderAddress
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from users.models import User
from django.http import HttpResponse
from users.models import UserWallet,UserTransactions
from django.db import transaction
from django.urls import reverse
from django.urls import reverse_lazy
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required(login_url='login')
def pay_order(request):
    success_url =  reverse_lazy('success_page')
    print(success_url)

    user = request.user
    cart = get_create_cart(user)
    items = Cart_items.objects.filter(cart=cart)
    address_id = request.POST.get('address_id')
    
    if not address_id:
        messages.error(request, "Please select an address")
        url=reverse('checkout')+'?cart=1'
        return redirect(url)
    address = get_object_or_404(Address, id=address_id, user=user)
    

    if not items.exists():
        messages.error(request, "Cart is empty")
        return redirect('cart_products')

    subtotal = sum(item.product.price * item.quantity for item in items)
    discount=request.session.get('coupon_discount')
    if discount:
        total=max(subtotal-discount,0)
    else:
        total=sum(item.product.price * item.quantity for item in items)
    success_url = request.build_absolute_uri(
        reverse('success_page')
    )
    cancel_url = request.build_absolute_uri(
        reverse('checkout')
    )
    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    mode='payment',
    customer_email=user.email,
    line_items=[{
        'price_data': {
            'currency': 'inr',
            'product_data': {'name': 'Order Payment'},
            'unit_amount': int(total * 100),
        },
        'quantity': 1,
    }],
    metadata={
        'user_id': str(user.id),
        'address_id': str(address.id),
    },
    success_url=success_url,

    
    cancel_url=cancel_url,
)       

   
    request.session['checkout_address_id'] = address.id
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    return redirect(session.url)

def success_page(request):
    # order=Order.objects.get(pk=pk)
    return render(request,'orders/success_page.html')
@login_required(login_url='login')
def order_items(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_items.html', {
        'orders': orders
    })



@csrf_exempt
def stripe_webhook(request):
    print(' WEBHOOK HIT')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
       print(" Stripe webhook verification failed:", e)
       return HttpResponse(status=400)


    
    print(event['type'])
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        user_id = session['metadata']['user_id']
        address_id = session['metadata']['address_id']
        amount = Decimal(session['amount_total']) / 100

        user = User.objects.get(id=user_id)
        address = Address.objects.get(id=address_id)

        cart_items = Cart_items.objects.filter(cart__user=user)
        order_address=OrderAddress.objects.create(
            user=user,
            phone=address.phone,
            pincode=address.pincode,
            place=address.place
        )
        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=amount,
            is_paid=True,
            stripe_session_id=session['id'],
            payment_method='stripe'
            
        )

        for item in cart_items:
            Order_item.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.quantity -= item.quantity
            item.product.save()

        cart_items.delete()

        
        wallet, _ = AdminWallet.objects.get_or_create(id=1)
        print(wallet)
        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            order=order,
            amount=amount
        )

    return HttpResponse(status=200)


def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = Order_item.objects.filter(order=order).select_related("product")

    if order.status == 'cancelled':
        messages.error(request, 'The order is already cancelled')
        return redirect('order_items')

    if order.status == 'delivered':
        messages.error(request, 'Delivered orders cannot be cancelled')
        return redirect('order_items')
    
    if order.status == 'shipped':
        messages.error(request, 'shipped orders cannot be cancelled')
        return redirect('order_items')
    
    if order.refund_to_wallet:
        messages.error(request, 'Refund already processed')
        return redirect('order_items')

    refund_amount = Decimal(order.total_amount)

    with transaction.atomic():

        
        order.status = 'cancelled'
        order.refund_to_wallet = True
        order.save(update_fields=["status", "refund_to_wallet"])

        
        wallet, _ = UserWallet.objects.get_or_create(user=request.user)
        wallet.balance += refund_amount
        wallet.save(update_fields=["balance"])

        
        if order.payment_method == 'stripe':
            admin_wallet = AdminWallet.objects.select_for_update().get(id=1)

            if admin_wallet.balance < refund_amount:
                raise ValueError("Admin wallet balance insufficient")

            admin_wallet.balance -= refund_amount
            admin_wallet.save(update_fields=["balance"])

        
        for item in items:
            product = item.product
            product.quantity += item.quantity
            product.save(update_fields=["quantity"])

       
        UserTransactions.objects.create(
            wallet=wallet,
            transaction_type='CREDIT',
            amount=refund_amount,
            description=f"Refund for Order #{order.id}"
        )

    messages.success(request, f"₹{refund_amount} refunded to your wallet")
    return redirect('order_items')

def wallet_view(request):
    wallet,created=UserWallet.objects.get_or_create(user=request.user)
    transactions=UserTransactions.objects.filter(
            wallet=wallet
    ).order_by('-created_at')
   
    
    return render(request, 'users/wallet.html', {
        'wallet': wallet,
        'transactions': transactions

    })
@login_required(login_url='login')
def wallet_pay_order(request):
    user=request.user
    cart=get_create_cart(user)
    items=Cart_items.objects.filter(cart=cart)
    address_id = request.POST.get('address_id')
    if not address_id:
        messages.error(request, "Please select an address")
        url=reverse('checkout')+'?cart=1'
        return redirect(url)
    address = get_object_or_404(Address, id=address_id, user=user)
    if not items.exists():
        messages.error(request,'your cart is empty')
        return redirect('cart_products')
    wallet,_=UserWallet.objects.get_or_create(user=user)
    total=sum(item.product.price *item.quantity for item in items)
    if wallet.balance<total:
        messages.error(request,'There is no sufficient balance')
        url=reverse('checkout')+'?cart=1'
        return redirect(url)
    with transaction.atomic():
        wallet.balance-=Decimal(total)
        wallet.save()

        order_address=OrderAddress.objects.create(
            user=user,
            phone=address.phone,
            pincode=address.pincode,
            place=address.place
        )
        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=total,
            is_paid=True,
            
            payment_method='wallet'
            
        )
        for item in items:
            product = item.product

            if product.quantity < item.quantity:
                raise ValueError("Insufficient stock")

            Order_item.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            product.quantity -= item.quantity
            product.save(update_fields=["quantity"])

        # user wallet transaction log (ONLY this)
        UserTransactions.objects.create(
            wallet=wallet,
            transaction_type='DEBIT',
            amount=total,
            description=f"Payment for Order #{order.id}"
        )

        items.delete()

    messages.success(request, "Order placed using wallet")
    return redirect('order_items')