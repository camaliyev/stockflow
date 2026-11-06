from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .services import add_order_item
from .forms import OrderForm, OrderItemForm
from .models import Order

@login_required(login_url="/admin/login/")
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()

            return redirect("orders:order_detail", pk=order.pk)
    else:
        form = OrderForm()

    return render(
        request,
        "orders/order_form.html",
        {"form": form},
    )


@login_required(login_url="/admin/login/")
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("created_by"),
        pk=pk,
    )
    items = order.items.select_related("product")

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "items": items,
        },
    )

@login_required(login_url="/admin/login/")
def order_item_add(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderItemForm(request.POST)

        if form.is_valid():
            try:
                add_order_item(
                    order_id=order.pk,
                    product_id=form.cleaned_data["product"].pk,
                    quantity=form.cleaned_data["quantity"],
                )
            except ValidationError as error:
                form.add_error(None, error)
            else:
                return redirect("orders:order_detail", pk=order.pk)
    else:
        form = OrderItemForm()

    return render(
        request,
        "orders/order_item_form.html",
        {
            "order": order,
            "form": form,
        },
    )