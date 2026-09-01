from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.maestros.models import Producto, Proveedor, Ubicacion


class Recepcion(TimeStampedModel):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='recepciones')
    numero_documento = models.CharField(max_length=50, blank=True)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recepciones',
    )

    class Meta:
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f'Recepción #{self.pk} - {self.proveedor}'


class RecepcionDetalle(TimeStampedModel):
    recepcion = models.ForeignKey(Recepcion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='+')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='+')
    cantidad = models.PositiveIntegerField()
    lote = models.CharField(max_length=50, blank=True, default='')
    fecha_vencimiento = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Detalle de recepción'
        verbose_name_plural = 'Detalles de recepción'

    def __str__(self):
        return f'{self.producto.sku} x{self.cantidad}'
