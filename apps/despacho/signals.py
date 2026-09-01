from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventario.models import Kardex, Stock

from .models import DespachoDetalle


@receiver(post_save, sender=DespachoDetalle)
def registrar_salida_kardex(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():
        stock, _ = Stock.objects.select_for_update().get_or_create(
            producto=instance.producto,
            ubicacion=instance.ubicacion,
            lote=instance.lote,
            defaults={'cantidad': 0},
        )
        stock_anterior = stock.cantidad
        stock.cantidad = max(stock.cantidad - instance.cantidad, 0)
        stock.save()

        Kardex.objects.create(
            tipo=Kardex.SALIDA,
            producto=instance.producto,
            ubicacion=instance.ubicacion,
            cantidad=instance.cantidad,
            stock_anterior=stock_anterior,
            stock_resultante=stock.cantidad,
            documento=f'Despacho #{instance.despacho_id}',
            usuario=instance.despacho.registrado_por,
        )
