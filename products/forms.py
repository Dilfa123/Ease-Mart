from django import forms
from .models import Products,CategoryModel,Images,Coupons

class ProductsForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=['title','discription','price','image','category']
        widgets = {
            'price': forms.NumberInput(attrs={'min': '1'})
        } 

    def clean_price(self):
        price=self.cleaned_data.get('price')
        if price < 1:
            raise forms.ValidationError('negative value is not applicable')
        return price
    def clean_title(self):
        title=self.cleaned_data.get('title')
        if title.replace(" ", "").isdigit():
            raise forms.ValidationError('Product name must be in alphabet')
        return title

class ProductEditForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=['title','price','category','quantity']
        widgets = {
            'price': forms.NumberInput(attrs={'min': '1'})
        }    

        def clean_price(self):
            price=self.cleaned_data.get('price')
            if price < 1:
                raise forms.ValidationError('negative value is not applicable')
            return price
       
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model=CategoryModel
        fields=['name']

    def clean_category(self):
        name=self.cleaned_data.get('name')
        if CategoryModel.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('this category name is already exist')
        return name
class CouponForm(forms.ModelForm):
    class Meta:
        model=Coupons
        fields=['code','discount','start_date','expire_date','min_purchase']
    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        max_discount = 1000

        if discount < 0:
            raise forms.ValidationError('Coupon cannot be less than zero')

        if discount < max_discount:
            raise forms.ValidationError('Discount cannot exceed ₹1000')

        return discount

