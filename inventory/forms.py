from django import forms

from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "price",
            "stock_quantity",
            "low_stock_threshold",
            "is_active"
        ]

class StockAdjustmentForm(forms.Form):
    quantity_change = forms.IntegerField(
        help_text="Use a positive number to add stock or a negative number to remove it.",
    )
    reason = forms.CharField(max_length=255)

    def clean_quantity_change(self):
        quantity_change = self.cleaned_data["quantity_change"]

        if quantity_change == 0:
            raise forms.ValidationError("Quantity change cannot be zero.")

        return quantity_change