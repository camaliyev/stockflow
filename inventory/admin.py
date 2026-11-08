from django.contrib import admin

from .models import Category, Product, StockMovement

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "low_stock",
        "is_active",
    )
    search_fields = ("name", "sku")
    list_filter = ("category", "is_active")
    readonly_fields = ("stock_quantity",)
    

    @admin.display(boolean=True, description="Low Stock")
    def low_stock(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity_change",
        "reason",
        "created_by",
        "created_at",
    )
    list_select_related = ("product", "created_by")
    search_fields = ("product__name", "product__sku", "reason")
    list_filter = ("created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False