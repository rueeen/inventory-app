from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=120, unique=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=160, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=160, unique=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.code if not self.name else f"{self.code} - {self.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    careers = models.ManyToManyField(Career, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Product(models.Model):
    ITEM_TYPES = [
        ("EQUIP", "Equipo"),
        ("SUP", "Insumo"),
        ("GLASS", "Material de vidrio"),
    ]

    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES, default="EQUIP")

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    technical_spec = models.TextField(blank=True)
    careers = models.ManyToManyField(Career, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True)

    unit_value_uf = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observations = models.TextField(blank=True)

    unit = models.CharField(max_length=30, default="unidad")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    min_stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"


class InventoryItem(models.Model):
    """Stock actual por producto y bodega."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("product", "warehouse")

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.quantity}"


class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJ = "ADJ"
    MOVEMENT_TYPES = [
        (IN, "Entrada"),
        (OUT, "Salida"),
        (ADJ, "Ajuste"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)

    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.created_at:%Y-%m-%d} {self.movement_type} "
            f"{self.product.sku} {self.quantity}"
        )
