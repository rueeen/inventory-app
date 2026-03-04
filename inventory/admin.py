from django.contrib import admin
from .models import Category, Warehouse, Supplier, Product, InventoryItem, StockMovement

admin.site.register(Category)
admin.site.register(Warehouse)
admin.site.register(Supplier)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "supplier", "min_stock", "active")
    search_fields = ("sku", "name")
    list_filter = ("active", "category")

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity")
    search_fields = ("product__sku", "product__name", "warehouse__name")

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "movement_type", "product", "warehouse", "quantity", "reason")
    search_fields = ("product__sku", "product__name", "reason")
    list_filter = ("movement_type", "warehouse")