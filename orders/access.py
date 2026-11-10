from .models import Order

def orders_visible_to(user):
    orders = Order.objects.all()

    if user.is_staff:
        return orders

    return orders.filter(created_by=user)