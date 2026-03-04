from django import forms

from .models import Product, Warehouse


class StockMovementForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    movement_type = forms.ChoiceField(
        choices=[("IN", "Entrada"), ("OUT", "Salida"), ("ADJ", "Ajuste")]
    )
    quantity = forms.IntegerField()
    reason = forms.CharField(required=False)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity == 0:
            raise forms.ValidationError("La cantidad no puede ser 0.")
        return quantity


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "item_type",
            "category",
            "supplier",
            "technical_spec",
            "unit",
            "unit_value_uf",
            "min_stock",
            "active",
            "observations",
        ]


class InventoryImportForm(forms.Form):
    file = forms.FileField(
        label="Archivo Excel (.xlsx)",
        help_text='Debe incluir hojas llamadas "Equipos" e "Insumos".',
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Solo se permiten archivos .xlsx")
        return uploaded_file
