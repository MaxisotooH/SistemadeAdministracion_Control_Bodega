from django import forms
from django.forms import inlineformset_factory

from .models import Recepcion, RecepcionDetalle


class RecepcionForm(forms.ModelForm):
    class Meta:
        model = Recepcion
        fields = ['proveedor', 'numero_documento', 'fecha', 'observaciones']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


RecepcionDetalleFormSet = inlineformset_factory(
    Recepcion,
    RecepcionDetalle,
    fields=['producto', 'ubicacion', 'cantidad', 'lote', 'fecha_vencimiento'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'ubicacion': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
        'lote': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
    },
)
