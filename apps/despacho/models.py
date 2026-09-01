from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel
from apps.inventario.models import Stock
from apps.maestros.models import Cliente, Producto, Ubicacion


class Despacho(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='despachos')
    numero_documento = models.CharField(max_length=50, blank=True)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='despachos',
    )

    class Meta:
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f'Despacho #{self.pk} - {self.cliente}'


class DespachoDetalle(TimeStampedModel):
    despacho = models.ForeignKey(Despacho, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='+')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='+')
    cantidad = models.PositiveIntegerField()
    lote = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Detalle de despacho'
        verbose_name_plural = 'Detalles de despacho'

    def __str__(self):
        return f'{self.producto.sku} x{self.cantidad}'

    def clean(self):
        if not (self.producto_id and self.ubicacion_id and self.cantidad):
            return
        disponible = Stock.objects.filter(
            producto=self.producto, ubicacion=self.ubicacion, lote=self.lote,
        ).values_list('cantidad', flat=True).first() or 0
        if self.cantidad > disponible:
            raise ValidationError(
                f'Stock insuficiente para {self.producto} en {self.ubicacion}: '
                f'disponible {disponible}, solicitado {self.cantidad}.'
            )
