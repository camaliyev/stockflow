from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import Product
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