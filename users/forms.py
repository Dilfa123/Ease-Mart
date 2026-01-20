from django import forms
import hashlib
from .models import User,Password,Address

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','password','email']
        widgets={'username':forms.TextInput(attrs={'autocomplete':'new-username'}),
                 'password':forms.PasswordInput(attrs={'autocomplete':'new-password'}),
                 'email': forms.EmailInput(attrs={
                'autocomplete': 'off'
            }),}

   
    def clean_username(self):
        username=self.cleaned_data.get('username')
        if username.isdigit():
            raise forms.ValidationError('username must not contain only numbers ')
        return username
class PasswordForm(forms.ModelForm):
    class Meta:
        model=Password
        fields=['newpass','cnfrm_pass']
    def clean(self):
        cleaned_data=super().clean()
        password=self.cleaned_data.get('newpass')
        nw_pass=self.cleaned_data.get('cnfrm_pass')
        if password!=nw_pass:
            raise forms.ValidationError('both the password want to be same')
        return cleaned_data
class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=['place','phone','pincode']
    def clean_phone(self):
        phone=self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('phone number contain only numbers')
        if len(phone)!=10:
            raise forms.ValidationError('phone number must contain 10 digits')
        return phone
    def clean_pincode(self):
        pincode=self.cleaned_data.get('pincode')
        if not pincode.isdigit():
            raise forms.ValidationError('pincode contain only numbers')
        if len(pincode)!=6:
            raise forms.ValidationError('pincode must contain 6 digits')
        return pincode