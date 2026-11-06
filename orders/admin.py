from django.contrib import admin

from .models import Order,  OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("product", "quantity", "unit_price", "subtotal")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("customer_name",)
    list_select_related = ("created_by",)
    inlines = (OrderItemInline,)

    readonly_fields = (
        "customer_name",
        "status",
        "created_by",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False