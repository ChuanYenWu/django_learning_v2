from django.forms import ModelForm
from django import forms

from catalog.models import Product, Order, OrderItem
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import datetime


from django.forms import formset_factory, ModelForm
from .models import Order, Product, OrderItem

class OrderForm(ModelForm):
    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        phone_regex = r'^\d{10}$'
        validator = RegexValidator(phone_regex, message="請輸入電話號(純數字)")
        try:
            validator(phone_number)
        except ValidationError as e:
            raise ValidationError(_("Invalid phone number: {}".format(e)))
        return phone_number
    class Meta:
        model = Order
        fields = ['buyer', 'phone']

class OrderItemForm(forms.Form):
    quantity = forms.IntegerField(initial=0, label='數量')
    #quantity = forms.IntegerField(initial=0, min_value=0,
    #                error_messages={'min_value':  _("請給於大於0的數值"),})
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise ValidationError("請給於大於0的數值")
        return quantity

class BaseOrderItemFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()
        total_quantity = sum(form.cleaned_data.get('quantity') or 0 for form in self.forms)
        if total_quantity <= 0:
            raise ValidationError('總數量必須大於 0')
            #raise forms.ValidationError('總數量必須大於 0')

"""
class OrderItemForm(ModelForm):
    quantity = forms.IntegerField(initial=0, min_value=0)
    name = forms.CharField(disabled=True)
    class Meta:
        model = Product
        fields = ['name', 'summary', 'cost']
"""

class CheckOrderForm(forms.Form):
    phone = forms.CharField(max_length=10, help_text='請輸入欲查詢之電話')



