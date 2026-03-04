from django import forms
from .models import Product, Warehouse

class StockMovementForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    movement_type = forms.ChoiceField(choices=[("IN","Entrada"),("OUT","Salida"),("ADJ","Ajuste")])
    quantity = forms.IntegerField()
    reason = forms.CharField(required=False)

    def clean_quantity(self):
        q = self.cleaned_data["quantity"]
        if q == 0:
            raise forms.ValidationError("La cantidad no puede ser 0.")
        return q