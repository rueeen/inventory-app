from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import Career, InventoryItem, Product, Subject, Warehouse


def _first_value(row, candidates, default=""):
    import pandas as pd

    for name in candidates:
        if name in row and pd.notna(row[name]):
            return str(row[name]).strip()
    return default


def _parse_int(value, default=0):
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(float(text.replace(",", ".")))
    except (TypeError, ValueError):
        return default


def _parse_decimal(value, default=Decimal("0")):
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return Decimal(text.replace(",", "."))
    except (InvalidOperation, ValueError):
        return default


def _split_tokens(value):
    text = str(value or "").strip()
    if not text:
        return []
    for separator in [";", "|"]:
        text = text.replace(separator, ",")
    return [token.strip() for token in text.split(",") if token.strip()]


@transaction.atomic
def import_inventory_from_excel(file_obj):
    import pandas as pd

    workbook = pd.read_excel(file_obj, sheet_name=["Equipos", "Insumos"], engine="openpyxl")

    warehouse, _ = Warehouse.objects.get_or_create(name="Principal")

    summary = {
        "rows_processed": 0,
        "products_created": 0,
        "products_updated": 0,
        "items_created": 0,
        "items_updated": 0,
        "errors": [],
    }

    for sheet_name, item_type in (("Equipos", "EQUIP"), ("Insumos", "SUP")):
        df = workbook.get(sheet_name)
        if df is None:
            summary["errors"].append(f"No se encontró la hoja {sheet_name}.")
            continue

        for idx, row in df.iterrows():
            try:
                sku = _first_value(row, ["Código Inventario", "SKU", "Codigo", "Código"])
                name = _first_value(row, ["Equipo", "Insumo", "Nombre"])

                if not sku or not name:
                    continue

                summary["rows_processed"] += 1

                defaults = {
                    "name": name,
                    "item_type": item_type,
                    "technical_spec": _first_value(
                        row,
                        ["Especificación Técnica Detallada", "Especificacion", "Detalle"],
                    ),
                    "unit_value_uf": _parse_decimal(
                        _first_value(row, ["Valor Unitario UF", "Valor UF", "Valor"], default="0")
                    ),
                    "observations": _first_value(row, ["Observaciones", "Observación"]),
                    "unit": _first_value(row, ["Unidad"], default="unidad") or "unidad",
                    "min_stock": _parse_int(
                        _first_value(row, ["Stock Mínimo", "Stock Minimo", "Mínimo"], default="0")
                    ),
                    "active": True,
                }

                product, created = Product.objects.update_or_create(sku=sku, defaults=defaults)
                if created:
                    summary["products_created"] += 1
                else:
                    summary["products_updated"] += 1

                careers = _split_tokens(
                    _first_value(row, ["Carrera(s) que utiliza", "Carrera", "Carreras"])
                )
                if careers:
                    product.careers.clear()
                    for career_name in careers:
                        career, _ = Career.objects.get_or_create(name=career_name)
                        product.careers.add(career)

                subjects = _split_tokens(
                    _first_value(
                        row,
                        ["Código(s)-Nombre(s) de Asignatura(s)", "Asignaturas", "Asignatura"],
                    )
                )
                if subjects:
                    product.subjects.clear()
                    for subject_token in subjects:
                        code = subject_token.split("-")[0].strip()
                        subject, _ = Subject.objects.get_or_create(code=code)
                        product.subjects.add(subject)

                quantity = _parse_int(
                    _first_value(row, ["Cantidad", "Stock", "Existencia"], default="0")
                )
                item, item_created = InventoryItem.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={"quantity": quantity},
                )
                if item_created:
                    summary["items_created"] += 1
                else:
                    item.quantity = quantity
                    item.save(update_fields=["quantity"])
                    summary["items_updated"] += 1
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(
                    f"{sheet_name} fila {idx + 2}: {exc}"
                )

    return summary
