from django.urls import path

from .views import (
    CreateMovementView,
    CreateProductView,
    DashboardView,
    ImportInventoryView,
    SetActiveCareerView,
)

app_name = "inventory"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("productos/nuevo/", CreateProductView.as_view(), name="create_product"),
    path("movimientos/nuevo/", CreateMovementView.as_view(), name="create_movement"),
    path("importar/", ImportInventoryView.as_view(), name="import_inventory"),
    path("carrera/activa/<int:career_id>/", SetActiveCareerView.as_view(), name="set_active_career"),
]
