from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Product

@login_required(login_url="/admin/login/")
def product_list(request):
    products = Product.objects.select_related("category").all()

    return render(
        request,
        "inventory/product_list.html",
        {"products": products}  
    )
