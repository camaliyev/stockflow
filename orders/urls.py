from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("add/", views.order_create, name="order_create"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/items/add/", views.order_item_add, name="order_item_add"),
]