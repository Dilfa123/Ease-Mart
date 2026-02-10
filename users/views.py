from django.shortcuts import get_object_or_404, render,redirect
from .forms import UserForm,PasswordForm,AddressForm
from .models import User,Otp,Pass_Otp,Admin_model,Address
from .otp import send_otp_via_email
import random
from django.contrib import messages
from products.models import Products,CategoryModel,Coupons
from django.views.decorators.cache import never_cache
import hashlib
from django.contrib.auth import authenticate, login
from products.forms import CouponForm
from products.views import error_page
from django.db.models.functions import Coalesce
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from orders.models import Order,Order_item
from django.utils import timezone
from orders.models import WalletTransaction,AdminWallet
from django.utils import timezone
from django.db.models import Sum,Count
from orders.models import Order_item
@never_cache
def signupview(req):
    if req.method == 'POST':
        form = UserForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            raw_pass = form.cleaned_data['password']
            user.set_password(raw_pass)
            user.is_active=False
            

            
            req.session['pending_user_id'] = user.id

            otp = str(random.randint(1000, 9999))
            Otp.objects.create(otp=otp, user=user)
            send_otp_via_email(user.email, otp)
            
            return redirect('otp')
    else:
        form = UserForm()

    return render(req, 'users/signup.html', {'form': form})


    #except:
#      return redirect('error_page')


@never_cache
def otpview(req):
    user_id = req.session.get('pending_user_id')

    if not user_id:
        messages.error(req, "Session expired. Signup again.")
        return redirect('signup')

    user = User.objects.get(id=user_id)
    otp_obj = Otp.objects.filter(user=user).last()

    if req.method == 'POST':
        user_otp = req.POST.get('otp')

        if otp_obj.otp == user_otp:
            user.is_active=True
            user.save()
            login(req, user, backend='django.contrib.auth.backends.ModelBackend')

            del req.session['pending_user_id']

            messages.success(req, "OTP Verified. You are logged in.")
            return redirect('home')

        else:
            messages.error(req, "Invalid OTP.")

    return render(req, 'users/otp.html')


    #except:
#      return redirect('error_page')
def resend_otp(req):
    #try:
       def resend_otp(req):
            user_id = req.session.get('pending_user_id')
            if not user_id:
                messages.error(req, "Session expired.")
                return redirect('signup')

            user = User.objects.get(id=user_id)
            otp = str(random.randint(1000, 9999))
            Otp.objects.create(user=user, otp=otp)
            send_otp_via_email(user.email, otp)

            messages.success(req, "OTP resent successfully")
            return redirect('otp')

    #except:
#      return redirect('error_page')

        
@never_cache
def loginview(req):
    #try:
        if req.method=='POST':
        
            username=req.POST.get('username')
            password=req.POST.get('password')
           
            user=authenticate(req,username=username,password=password)
            
            if user is not None:
                
                if not user.is_active:
                     messages.error(req,'you are not allowed to this site')
                     req.session.flush()
                     return redirect('error_page')
                login(req,user)
                return redirect('home')
            
        return render(req,'users/login.html')
    #except:
#      return redirect('error_page')
def forget_pass(req):
    #try:
        if req.method=='POST':

            email=req.POST.get('email')
            user=User.objects.filter(email=email).first()
            if user:
            
                otp=str(random.randint(10000,99999))
                Pass_Otp.objects.create(user=user,otp=otp)
                send_otp_via_email(email,otp)
                req.session['reset_user_id']=user.id
                return redirect('forget_otp')
        return render(req,'users/forget_pass.html')
    #except:
#      return redirect('error_page')
def forget_otp(req):
    #try:
        if req.method=='POST':
            user_otp=req.POST.get('otp')
            real_otp=Pass_Otp.objects.last().otp
            if real_otp==user_otp:
                messages.success(req,'correct otp')
                return redirect('confirm_pass')
            else:
                messages.error(req,'invalid otp')
        return render(req,'users/otp.html')
    #except:
#      return redirect('error_page')
def confirm_pass(req):
    #try:
        if req.method=='POST':
            form=PasswordForm(req.POST)
            if form.is_valid():
                newpass=form.cleaned_data.get('newpass')
                user_id=req.session.get('reset_user_id')
                user=User.objects.get(id=user_id)
                user.password=newpass
                user.save()
                messages.success(req,'password updated')
                return redirect('login')
            
        else:
            form=PasswordForm()
        return render(req,'users/confirm_password.html',{'form':form})
    #except:
#      return redirect('error_page')
@never_cache
def logout_view(request):
    #try:
        request.session.flush()
        return redirect('home')
    #except:
#      return redirect('error_page')
#

@never_cache

def admin_login(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        admin = Admin_model.objects.filter(username=username, password=password).first()
        if admin:
            req.session['admin_id'] = admin.id
            req.session['username'] = admin.username
            
            return redirect('admin_dashboard')
    return render(req, 'admin/admin_login.html')
    # except:
    #     return error_page


# ----------------------------------------------
@never_cache
@login_required(login_url='admin_login')
def admin_dashboard(req):
    today=timezone.now().date()
    now=timezone.now()
    base_revenue=Order.objects.filter(
         is_paid=True
    ).exclude(status='cancelled')
    #total revenue

    total_revenue=base_revenue.aggregate(
         total=Sum('total_amount')
    )['total'] or 0

    #stripe revenue
    stripe_revenue=base_revenue.filter(
         payment_method='stripe'
    ).aggregate(
         total=Sum('total_amount')
    )['total'] or 0
    #wallet revenue
    wallet_revenue=base_revenue.filter(
         payment_method='wallet'
    ).aggregate(
         total=Sum('total_amount')
    )['total'] or 0
    #today's revenue
    today_revenue=base_revenue.filter(
         created_at__date=today
    ).aggregate(
         total=Sum('total_amount')
    )['total'] or 0
    #monthly revenue
    monthly_revenue=base_revenue.filter(
         created_at__year=now.year,
         created_at__month=now.month
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    total_orders = base_revenue.count()
    stripe_orders = base_revenue.filter(payment_method='stripe').count()
    wallet_orders = base_revenue.filter(payment_method='wallet').count()
    top_categories = (
    Order_item.objects
    .filter(
        order__is_paid=True
    )
    .exclude(order__status='cancelled')
    .values('product__category__name')
    .annotate(
        total_sold=Coalesce(Sum('quantity'), 0)
    )
    .order_by('-total_sold')[:5]
)
    context = {
        'total_revenue': total_revenue,
        'stripe_revenue': stripe_revenue,
        'wallet_revenue': wallet_revenue,
        'today_revenue': today_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'stripe_orders': stripe_orders,
        'wallet_orders': wallet_orders,
        'top_categories': top_categories,
    }
    

    return render(req, 'admin/dashboard.html',context)
   

@never_cache
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def admin_user(req):
    #try:
        if not req.session.get('admin_id'):
            return redirect('admin_login')
        
        users=User.objects.all()
        q=req.GET.get('q')
        if q:
             users=users.filter(username__icontains=q)
        sort_options=req.GET.get('sort')
    
        if sort_options=='Active':
            users=users.order_by('-is_active')
        elif sort_options=='Inactive':
            users=users.order_by('is_active')
       
             

        return render(req,'admin/admin_user_list.html',{'users':users})
    #except:
    
#      return redirect('error_page')
@never_cache
def admin_user_block(request,pk):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     user=User.objects.get(pk=pk)
     user.is_active=False
     user.save()
     return redirect('admin_user')
@never_cache
def admin_user_unblock(request,pk):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     user=User.objects.get(pk=pk)
     user.is_active=True
     user.save()
     return redirect('admin_user')

     
@never_cache
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def admin_product_list(req):
    #try:
        if not req.session.get('admin_id'):
            return redirect('admin_login')
        
        products=Products.objects.filter(is_delete=False,category__is_delete=False)
        return render(req,'admin/admin_product_list.html',{'products':products})

    #except:
#      return redirect('error_page')
@never_cache
def admin_category_list(req):
    #try:
    
        if not req.session.get('admin_id'):
            return redirect('admin_login')
    
        categories=CategoryModel.objects.filter(is_delete=False)
        return render(req,'admin/admin_category_list.html',{'categories':categories})
    #except:
#      return redirect('error_page')
@never_cache
@login_required(login_url='admin_login')
def soft_deleted_products(request):
     products=Products.objects.filter(Q(is_delete=True)|Q(category__is_delete=True))
     
     return render(request,'admin/soft_deleted_products.html',{'products':products})
def restore_products(request,pk):
     if request.method=='POST':
        product = get_object_or_404(Products, pk=pk)
        if product.category and product.category.is_delete:
             product.category.is_delete=False
             product.category.save()
        elif product:
             product.is_delete=False
             product.save()
        return redirect('soft_deleted_products')
@never_cache
def admin_detail_category(req,pk):
    #try:
        if not req.session.get('admin_id'):
            return redirect('admin_login')
    
        category=get_object_or_404(CategoryModel,pk=pk)
        products=Products.objects.filter(category=category,is_delete=False)
        return render(req,'admin/admin_one_category.html'
                    ,{'products':products,
                    'category':category})
    #except:
#      return redirect('error_page')
# 
def admin_coupon_list(request):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     today = timezone.now().date()
     Coupons.objects.filter(
        is_active=True,
        expire_date__lt=today
    ).update(is_active=False)

   
     Coupons.objects.filter(
        is_active=False,
        start_date__lte=today,
        expire_date__gte=today
    ).update(is_active=True)
     coupons = Coupons.objects.all().order_by('-created_on')

     return render(request, 'admin/admin_coupon_list.html', {
        'coupons': coupons
    })
def admin_coupon_add(request):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     if request.method=='POST':
          form=CouponForm(request.POST)
          if form.is_valid():
               form.save()
               return redirect('admin_coupon_list')
     form=CouponForm()
     return render(request,'admin/admin_coupon_add.html',{'form':form})
               
def admin_coupon_edit(request,pk):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     coupon=get_object_or_404(Coupons,pk=pk)
     if request.method=='POST':
          form=CouponForm(request.POST,instance=coupon)
          if form.is_valid():
               form.save()
               return redirect('admin_coupon_list')
     form=CouponForm(instance=coupon)
     return render(request,'admin/admin_coupon_edit.html',{'form':form})
def admin_coupon_delete(request,pk):
     if not request.session.get('admin_id'):
          return redirect('admin_login')
     coupon=Coupons.objects.get(pk=pk)
     
     coupon.delete()
     return redirect('admin_coupon_list')
# def admin_coupon_toggle(request,pk):
#      if not request.session.get('admin_id'):
#           return redirect('admin_login')
#      coupons=Coupons.objects.get(pk=pk)
#      coupons.is_active=not coupons.is_active
#      coupons.save()
#      return redirect('admin_coupon_list')
@login_required(login_url='admin_login')
def admin_order_list(request):
     orders=Order.objects.all().prefetch_related('items__product').order_by('-created_at')
     
     return render(request,'admin/admin_order_list.html',{'orders':orders})
def admin_order_list_detail(request,pk):
     orders=Order.objects.get(pk=pk)
     items=Order_item.objects.filter(order=orders)
     return render(request,'admin/admin_order_list_detail.html',{'orders':orders,'items':items})

def admin_wallet(request):
     wallet,create=AdminWallet.objects.get_or_create(id=1)
     transactions=WalletTransaction.objects.select_related('order').order_by('-created_at')
     return render(request,'admin/admin_wallet.html',{'wallet':wallet,'transactions':transactions})
def admin_status_change(request,pk):
     order=get_object_or_404(Order,pk=pk)
     if request.method=='POST':
          new_status=request.POST.get('status')
          order.status=new_status
          order.save()
     return redirect('admin_order_list')
     
# ----------------------------------------
@never_cache
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def admin_logout(req):
    req.session.flush()  
    return redirect('admin_login')
    
    #except:
#      return redirect('error_page')

@login_required(login_url='login')
def user_detail(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/user_detail.html', {
        'orders': orders
    })

    #except:
#      return redirect('error_page')
@login_required(login_url='login')
def user_address_register(request):
    
     if request.method=='POST':
          form=AddressForm(request.POST)
          if form.is_valid():
               address=form.save(commit=False)
               address.user=request.user
               address.save()
               return redirect('show_address')
     else:
          form=AddressForm()
     return render(request,'users/user_address_register.html',{'form':form})
@login_required(login_url='login')
def show_address(request):
     address=Address.objects.filter(user=request.user)
     return render(request,'users/show_address.html',{'address':address})
def edit_address(request,pk):
     if not request.user.is_authenticated:
          return redirect('login')
     address=get_object_or_404(Address,pk=pk)
     if request.method=='POST':
          
          form=AddressForm(request.POST,instance=address)
          if form.is_valid():
               form.save()
               return redirect('show_address')
     else:   
        form=AddressForm(instance=address)
     return render(request,'users/edit_address.html',{'form':form})
def delete_address(request,pk):
     
     if not request.user.is_authenticated:
          return redirect('login')
     
     address=Address.objects.get(pk=pk)  
     address.delete()
     return redirect('show_address')
