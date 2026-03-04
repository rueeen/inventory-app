from django.db import transaction
from django.db.models import F

from .models import InventoryItem, StockMovement


@transaction.atomic
def apply_stock_movement(*, product, warehouse, movement_type, quantity, reason=""):
    """Crea el movimiento y actualiza el stock de forma atómica."""
    if movement_type in ("IN", "OUT") and quantity <= 0:
        raise ValueError("Para IN/OUT, quantity debe ser positiva.")

    delta = quantity
    if movement_type == "OUT":
        delta = -quantity

    movement = StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
    )

    item, _ = InventoryItem.objects.select_for_update().get_or_create(
        product=product,
        warehouse=warehouse,
        defaults={"quantity": 0},
    )

    InventoryItem.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)
    item.refresh_from_db()

    if item.quantity < 0:
        raise ValueError("Stock insuficiente: el movimiento dejaría el stock negativo.")

    return movement, item
