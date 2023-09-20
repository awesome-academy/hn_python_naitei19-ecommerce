from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext as _

from .models import User
from .constants import PAYMENT_CHOICES

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)
    

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] 
   
class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=True)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label=_("(select country)")).formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }),
        initial='VN'
        )
    shipping_zip = forms.CharField(required=True)

    billing_address = forms.CharField(required=True)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label=_("(select country)")).formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }),
        initial='VN'
        )
    billing_zip = forms.CharField(required=True)

    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Promo code'),
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))

class PaymentForm(forms.Form):
    card_number = forms.CharField(required=True)
