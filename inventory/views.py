from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q

from .models import Category, Product

@login_required(login_url="/admin/login/")
def product_list(request):
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    categories = Category.objects.all()
    products = Product.objects.select_related("category").all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    selected_category = categories.filter(
        pk=category_id
    ).first() if category_id.isdecimal() else None

    if selected_category:
        products = products.filter(category=selected_category)

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products,
            "search_query": search_query,
            "categories": categories,
            "selected_category": selected_category,
        },
    )