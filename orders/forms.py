from django import forms

from .models import Order
from inventory.models import Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name"]


class OrderItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
    )
    quantity = forms.IntegerField(min_value=1)