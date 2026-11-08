from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import Product
from inventory.services import adjust_stock
from .models import Order, OrderItem


@transaction.atomic
def add_order_item(*, order_id, product_id, quantity):
    order = Order.objects.select_for_update().get(pk=order_id)

    if order.status != Order.Status.DRAFT:
        raise ValidationError("Only draft orders can be edited.")

    if quantity < 1:
        raise ValidationError("Quantity must be at least one.")

    product = Product.objects.select_for_update().get(pk=product_id)

    if not product.is_active:
        raise ValidationError("This product is inactive.")

    if order.items.filter(product=product).exists():
        raise ValidationError("This product is already in the order.")

    item = OrderItem(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )
    item.full_clean()
    item.save()

    return item

@transaction.atomic
def update_order_item_quantity(*, order_id, item_id, quantity):
    order = Order.objects.select_for_update().get(pk=order_id)

    if order.status != Order.Status.DRAFT:
        raise ValidationError("Only draft orders can be edited.")

    if quantity < 1:
        raise ValidationError("Quantity must be at least one.")

    item = OrderItem.objects.get(
        pk=item_id,
        order=order,
    )

    item.quantity = quantity
    item.full_clean()
    item.save(update_fields=["quantity"])

    return item

@transaction.atomic
def remove_order_item(*, order_id, item_id):
    order = Order.objects.select_for_update().get(pk=order_id)

    if order.status != Order.Status.DRAFT:
        raise ValidationError("Only draft orders can be edited.")

    item = OrderItem.objects.get(
        pk=item_id,
        order=order,
    )

    item.delete()

@transaction.atomic
def confirm_order(*, order_id, user):
    order = Order.objects.select_for_update().get(pk=order_id)

    if order.status != Order.Status.DRAFT:
        raise ValidationError("Only draft orders can be confirmed.")

    items = list(order.items.all())

    if not items:
        raise ValidationError("Add at least one item before confirming.")

    product_ids = [item.product_id for item in items]

    products = {
        product.pk: product
        for product in Product.objects.select_for_update()
        .filter(pk__in=product_ids)
        .order_by("pk")
    }

    for item in items:
        product = products[item.product_id]

        if not product.is_active:
            raise ValidationError(
                f"{product.name} is inactive."
            )

        if product.stock_quantity < item.quantity:
            raise ValidationError(
                f"Not enough stock for {product.name}."
            )

    for item in items:
        adjust_stock(
            product_id=item.product_id,
            quantity_change=-item.quantity,
            reason=f"Order #{order.pk} confirmed",
            user=user,
            order=order,
        )

    order.status = Order.Status.CONFIRMED
    order.save(update_fields=["status"])

    return order