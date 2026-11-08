from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Product, StockMovement

@transaction.atomic
def adjust_stock(*, product_id, quantity_change, reason, user, order=None):
    product = Product.objects.select_for_update().get(pk=product_id)

    if quantity_change == 0:
        raise ValidationError("Quantity change cannot be zero")

    new_quantity = product.stock_quantity + quantity_change

    if new_quantity < 0:
        raise ValidationError("Not Enough stock for this adjustment.")

    movement = StockMovement(
        product=product,
        order=order,
        created_by=user,
        quantity_change=quantity_change,
        reason=reason,
    )
    movement.full_clean()

    product.stock_quantity = new_quantity
    product.save(update_fields=["stock_quantity"])

    movement.save()
    return movement