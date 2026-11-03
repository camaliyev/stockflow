from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Category, Product, StockMovement
from .services import adjust_stock


class StockAdjustmentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testworker",
            password="test-password",
        )
        self.category = Category.objects.create(name="T-shirts")
        self.product = Product.objects.create(
            name="Black T-shirt",
            sku="TSHIRT-TEST",
            category=self.category,
            price=Decimal("30.00"),
            stock_quantity=0,
        )

    def test_adding_stock_saves_movement(self):
        adjust_stock(
            product_id=self.product.pk,
            quantity_change=15,
            reason="New delivery",
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 15)
        self.assertEqual(
            StockMovement.objects.filter(product=self.product).count(),
            1,
        )

        movement = StockMovement.objects.get(product=self.product)

        self.assertEqual(movement.quantity_change, 15)
        self.assertEqual(movement.reason, "New delivery")
        self.assertEqual(movement.created_by, self.user)