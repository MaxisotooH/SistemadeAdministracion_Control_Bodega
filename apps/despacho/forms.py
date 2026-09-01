from collections import defaultdict

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.inventario.models import Stock

from .models import Despacho, DespachoDetalle


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['cliente', 'numero_documento', 'fecha', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class DespachoDetalleBaseFormSet(BaseInlineFormSet):
    def clean(self):
        # DespachoDetalle.clean() valida cada linea contra el stock actual,
        # pero no ve otras lineas del mismo despacho: dos lineas del mismo
        # producto+ubicacion podrian pasar cada una por separado y juntas
        # superar el disponible. Este chequeo agregado cubre ese caso.
        super().clean()
        if any(self.errors):
            return

        totales = defaultdict(int)
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            producto = form.cleaned_data.get('producto')
            ubicacion = form.cleaned_data.get('ubicacion')
            cantidad = form.cleaned_data.get('cantidad') or 0
            lote = form.cleaned_data.get('lote') or ''
            if producto and ubicacion:
                totales[(producto, ubicacion, lote)] += cantidad

        for (producto, ubicacion, lote), cantidad_total in totales.items():
            disponible = Stock.objects.filter(
                producto=producto, ubicacion=ubicacion, lote=lote,
            ).values_list('cantidad', flat=True).first() or 0
            if cantidad_total > disponible:
                raise ValidationError(
                    f'Stock insuficiente para {producto} en {ubicacion}: '
                    f'disponible {disponible}, solicitado en total {cantidad_total}.'
                )


DespachoDetalleFormSet = inlineformset_factory(
    Despacho,
    DespachoDetalle,
    formset=DespachoDetalleBaseFormSet,
    fields=['producto', 'ubicacion', 'cantidad', 'lote'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'ubicacion': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
        'lote': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
    },
)
