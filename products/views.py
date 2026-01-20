from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from .models import Products,CategoryModel,Images,Coupons
from .forms import ProductsForm,CategoryForm,ProductEditForm
from django.views.decorators.cache import never_cache
from django.db.models import Q
from users.models import Address
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
@never_cache
def homeview(request):
    # try:
        is_logged_in=False
        selected_cat_id=request.GET.get('category')
        cat=CategoryModel.objects.filter(is_delete=False)
        products=Products.objects.filter( is_delete=False,
        category__is_delete=False)
        q=request.GET.get('q')
       
        if q:
            products=products.filter(Q(title__icontains=q)|Q(category__name__icontains=q))
        if selected_cat_id not in (None, "", "None"):
            products = products.filter(category_id=selected_cat_id)

        sort_options=request.GET.get('sort')
    
        if sort_options=='High price':
            products=products.order_by('price')
        elif sort_options=='Low price':
            products=products.order_by('-price')
        elif sort_options=='name asc':
            products=products.order_by('title')
        elif sort_options=='name dec':
            products=products.order_by('-title')
        
            if request.session.get('username'):
                is_logged_in=True

        paginator = Paginator(products, 8)
        page_number=request.GET.get('page')
        page_obj=paginator.get_page(page_number)

        return render(request,'products/home.html',{'products':page_obj,
                                                    'cat':cat,
                                                'selected_cat_id':selected_cat_id,'is_logged_in':is_logged_in,
                                                'page_obj':page_obj}
                                                )
    # except:
    #     return redirect('error_page')


def category_page(request,pk):
    try:
        category=get_object_or_404(CategoryModel,pk=pk)
        products=Products.objects.filter(category=category,is_delete=False)
        return render(request,'products/category_one_products.html'
                    ,{'products':products,
                  'category':category})
    except:
        return redirect('error_page')
def add_category(request):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form=CategoryForm()
    return render(request,'products/add_category.html',{'form':form})
def edit_category(request,pk):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    category=CategoryModel.objects.get(pk=pk)
    if request.method=='POST':
        form=CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form=CategoryForm(request.POST)
    return render(request,'products/edit_category.html',{'form':form})


def delete_category(request,pk):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    if request.method=='POST':
        category=CategoryModel.objects.get(pk=pk)
        category.is_delete=True
        category.save()
        return redirect('admin_category_list')
    return render(request,'products/delete_category.html')


def error_page(request):
    return render(request,'products/error_page.html')

def add_product(request):
    if not request.session.get('admin_id'):
        return redirect('admin_login')

    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES)

        if form.is_valid():  
            product = form.save()

            extra_images = request.FILES.getlist('multi_images')
            for img in extra_images:
                Images.objects.create(product=product, image=img)

            return redirect('admin_product_list')
    else:
        form = ProductsForm()

    return render(request, 'products/product_register.html', {
        'form': form
    })

def edit_product(request,pk):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    product=get_object_or_404(Products,pk=pk)
    if request.method=='POST':
        form=ProductEditForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_product_list')
    else:
        form=ProductEditForm(instance=product)
    return render(request,'products/edit_product.html',{'form':form})


def delete_product(request,pk):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    product=get_object_or_404(Products,pk=pk)
    if request.method=='POST':
        product.is_delete=True
        product.save()
        return redirect('admin_product_list')
    return render(request,'products/delete_product.html')
def product_detail(request,pk):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    product=get_object_or_404(Products,pk=pk)
    images=Images.objects.filter(product=product)
    return render(request,'products/product_detail.html',{'product':product,'images':images})

def user_single_product(request,pk):
    product=get_object_or_404(Products,pk=pk)
    images=Images.objects.filter(product=product)
    product_url=request.build_absolute_uri(
        reverse('user_single_product',args=[product.pk])
    )

    return render(request,'products/user_single_product.html',{'product':product,'images':images,'product_url':product_url})

