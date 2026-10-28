from django.urls import path

from . import views

app_name = "Inventory"

urlpatterns = [
    path("products/", views.product_list, name="product_list")
]