from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.maestros.models import Producto, Ubicacion


class Stock(TimeStampedModel):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='stocks')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='stocks')
    lote = models.CharField(max_length=50, blank=True, default='')
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Stock'
        unique_together = ('producto', 'ubicacion', 'lote')
        ordering = ['producto__nombre', 'ubicacion']

    def __str__(self):
        return f'{self.producto.sku} @ {self.ubicacion} = {self.cantidad}'


class Kardex(TimeStampedModel):
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'
    TIPO_CHOICES = [(ENTRADA, 'Entrada'), (SALIDA, 'Salida')]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='movimientos')
    cantidad = models.PositiveIntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_resultante = models.PositiveIntegerField()
    documento = models.CharField(max_length=100, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='movimientos_kardex', null=True, blank=True,
    )

    class Meta:
        verbose_name_plural = 'Kardex'
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.tipo} {self.producto.sku} x{self.cantidad}'
