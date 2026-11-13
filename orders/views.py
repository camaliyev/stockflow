from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from .services import add_order_item, update_order_item_quantity, remove_order_item, confirm_order, cancel_order
from .forms import OrderForm, OrderItemForm, OrderItemQuantityForm
from .models import Order, OrderItem
from decimal import Decimal
from .access import orders_visible_to

@login_required
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


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        orders_visible_to(request.user).select_related("created_by"),
        pk=pk,
    )
    items = order.items.select_related("product")

    order_total = sum(
        (item.subtotal for item in items),
        Decimal("0.00"),
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "items": items,
            "order_total": order_total,
        },
    )

@login_required
def order_item_add(request, pk):
    order = get_object_or_40(
        orders_visible_to(request.user),
        pk=pk,
    )

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


@login_required
def order_item_update(request, pk, item_id):
    order = get_object_or_404(
        orders_visible_to(request.user),
        pk=pk,
    )
    item = get_object_or_404(
        OrderItem.objects.select_related("product"),
        pk=item_id,
        order=order,
    )

    if request.method == "POST":
        form = OrderItemQuantityForm(request.POST)

        if form.is_valid():
            try:
                update_order_item_quantity(
                    order_id=order.pk,
                    item_id=item.pk,
                    quantity=form.cleaned_data["quantity"],
                )
            except ValidationError as error:
                form.add_error(None, error)
            else:
                return redirect("orders:order_detail", pk=order.pk)
    else:
        form = OrderItemQuantityForm(
            initial={"quantity": item.quantity},
        )

    return render(
        request,
        "orders/order_item_quantity_form.html",
        {
            "order": order,
            "item": item,
            "form": form,
        },
    )

@login_required
def order_item_remove(request, pk, item_id):
    order = get_object_or_404(
        orders_visible_to(request.user),
        pk=pk,
    )
    item = get_object_or_404(
        OrderItem.objects.select_related("product"),
        pk=item_id,
        order=order,
    )

    error_message = None

    if request.method == "POST":
        try:
            remove_order_item(
                order_id=order.pk,
                item_id=item.pk,
            )
        except ValidationError as error:
            error_message = " ".join(error.messages)
        else:
            return redirect("orders:order_detail", pk=order.pk)

    return render(
        request,
        "orders/order_item_confirm_remove.html",
        {
            "order": order,
            "item": item,
            "error_message": error_message,
        },
    )

@login_required
def order_confirm(request, pk):
    order = get_object_or_404(
        orders_visible_to(request.user),
        pk=pk,
    )
    error_message = None

    if request.method == "POST":
        try:
            confirm_order(
                order_id=order.pk,
                user=request.user,
            )
        except ValidationError as error:
            error_message = " ".join(error.messages)
        else:
            return redirect("orders:order_detail", pk=order.pk)

    return render(
        request,
        "orders/order_confirm.html",
        {
            "order": order,
            "error_message": error_message,
        },
    )

@login_required
def order_cancel(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied(
            "Only staff members can cancel orders."
        )
    order = get_object_or_404(Order, pk=pk)
    error_message = None

    if request.method == "POST":
        try:
            cancel_order(
                order_id=order.pk,
                user=request.user,
            )
        except ValidationError as error:
            error_message = " ".join(error.messages)
        else:
            return redirect("orders:order_detail", pk=order.pk)

    return render(
        request,
        "orders/order_cancel.html",
        {
            "order": order,
            "error_message": error_message,
        },
    )

@login_required
def order_list(request):
    orders = orders_visible_to(request.user).select_related("created_by")

    return render(
        request,
        "orders/order_list.html",
        {"orders": orders},
    )