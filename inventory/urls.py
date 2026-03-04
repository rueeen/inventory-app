from django.urls import path
from .views import DashboardView, CreateMovementView, SetActiveCareerView

app_name = "inventory"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("movimientos/nuevo/", CreateMovementView.as_view(), name="create_movement"),
    path("carrera/activa/<int:career_id>/", SetActiveCareerView.as_view(), name="set_active_career"),
]