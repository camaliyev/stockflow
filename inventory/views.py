from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .models import Category, Product
from .forms import ProductForm, StockAdjustmentForm

from django.core.exceptions import ValidationError, PermissionDenied
from .services import adjust_stock

@login_required
def product_list(request):
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    categories = Category.objects.all()
    products = Product.objects.select_related("category").all()

    if not request.user.is_staff:
        products = products.filter(
            is_active=True,
            stock_quantity__gt=0,
        )

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

@login_required
def product_detail(request, pk):
    products = Product.objects.select_related("category")

    if not request.user.is_staff:
        products = products.filter(
            is_active=True,
            stock_quantity__gt=0,
        )

    product = get_object_or_404(products, pk=pk)

    stock_movements = None

    if request.user.is_staff:
        stock_movements = product.stock_movements.select_related(
            "created_by"
        )

    return render(
        request,
        "inventory/product_detail.html",
        {
            "product": product,
            "stock_movements": stock_movements,
        }
    )

@login_required
def product_create(request):
    if not request.user.is_staff:
        raise PermissionDenied("Only the business admin can manage inventory.")
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

@login_required
def product_update(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied("Only the business admin can manage inventory.")
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

@login_required
def stock_adjustment(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied("Only the business admin can manage inventory.")
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)

        if form.is_valid():
            try:
                adjust_stock(
                    product_id=product.pk,
                    quantity_change=form.cleaned_data["quantity_change"],
                    reason=form.cleaned_data["reason"],
                    user=request.user,
                )
            except ValidationError as error:
                form.add_error(None, error)
            else:
                return redirect(
                    "inventory:product_detail",
                    pk=product.pk,
                )
    else:
        form = StockAdjustmentForm()

    return render(
        request,
        "inventory/stock_adjustment.html",
        {
            "product": product,
            "form": form,
        },
    )