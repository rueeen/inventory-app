from django.shortcuts import get_object_or_404
from .models import Career
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import StockMovementForm
from .models import InventoryItem
from .services import apply_stock_movement


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.select_related(
            "product", "warehouse").order_by("product__sku", "warehouse__name")
        return render(request, "inventory/dashboard.html", {"items": items})


class CreateMovementView(LoginRequiredMixin, View):
    def get(self, request):
        form = StockMovementForm()
        return render(request, "inventory/create_movement.html", {"form": form})

    def post(self, request):
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                movement, item = apply_stock_movement(
                    product=form.cleaned_data["product"],
                    warehouse=form.cleaned_data["warehouse"],
                    movement_type=form.cleaned_data["movement_type"],
                    quantity=form.cleaned_data["quantity"],
                    reason=form.cleaned_data.get("reason", ""),
                )
                messages.success(
                    request, f"Movimiento registrado. Stock actual: {item.quantity}")
                return redirect("inventory:dashboard")
            except Exception as e:
                messages.error(request, str(e))
        return render(request, "inventory/create_movement.html", {"form": form})


class SetActiveCareerView(LoginRequiredMixin, View):
    def get(self, request, career_id):
        c = get_object_or_404(Career, id=career_id)
        # Solo permitir carreras asignadas (o staff)
        if request.user.is_staff or request.user.userprofile.careers.filter(id=c.id).exists():
            request.session["active_career_id"] = c.id
        return redirect("inventory:dashboard")
