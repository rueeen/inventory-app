from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import InventoryImportForm, StockMovementForm
from .importers import import_inventory_from_excel
from .models import Career, InventoryItem
from .services import apply_stock_movement


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.select_related("product", "warehouse").order_by(
            "product__sku", "warehouse__name"
        )
        return render(request, "inventory/dashboard.html", {"items": items})


class CreateMovementView(LoginRequiredMixin, View):
    def get(self, request):
        form = StockMovementForm()
        return render(request, "inventory/create_movement.html", {"form": form})

    def post(self, request):
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                _, item = apply_stock_movement(
                    product=form.cleaned_data["product"],
                    warehouse=form.cleaned_data["warehouse"],
                    movement_type=form.cleaned_data["movement_type"],
                    quantity=form.cleaned_data["quantity"],
                    reason=form.cleaned_data.get("reason", ""),
                )
                messages.success(request, f"Movimiento registrado. Stock actual: {item.quantity}")
                return redirect("inventory:dashboard")
            except Exception as exc:  # noqa: BLE001
                messages.error(request, str(exc))
        return render(request, "inventory/create_movement.html", {"form": form})


class ImportInventoryView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para importar inventario.")
        return redirect("inventory:dashboard")

    def get(self, request):
        return render(request, "inventory/import_inventory.html", {"form": InventoryImportForm()})

    def post(self, request):
        form = InventoryImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "inventory/import_inventory.html", {"form": form})

        summary = import_inventory_from_excel(form.cleaned_data["file"])
        messages.success(request, "Importación finalizada.")
        if summary["errors"]:
            messages.warning(request, f"La importación terminó con {len(summary['errors'])} advertencias.")

        return render(
            request,
            "inventory/import_inventory.html",
            {
                "form": InventoryImportForm(),
                "summary": summary,
            },
        )


class SetActiveCareerView(LoginRequiredMixin, View):
    def get(self, request, career_id):
        career = get_object_or_404(Career, id=career_id)
        profile = getattr(request.user, "userprofile", None)

        if request.user.is_staff or (profile and profile.careers.filter(id=career.id).exists()):
            request.session["active_career_id"] = career.id

        return redirect("inventory:dashboard")
