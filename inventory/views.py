from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .models import Category, Product
from .forms import ProductForm

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

@login_required(login_url="/admin/login/")
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk
    )

    return render(
        request,
        "inventory/product_detail.html",
        {"product": product},
    )

@login_required(login_url="/admin/login/")
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save()
            return redirect("inventory:product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(
        request,
        "inventory/product_form.html",
        {"form": form},
    )

@login_required(login_url="/admin/login/")
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("inventory:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "product": product,
        },
    )