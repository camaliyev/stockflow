from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q

from .models import Product

@login_required(login_url="/admin/login/")
def product_list(request):
    search_query = request.GET.get("q", "").strip()

    products = Product.objects.select_related("category").all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products,
            "search_query": search_query,
        },
    )