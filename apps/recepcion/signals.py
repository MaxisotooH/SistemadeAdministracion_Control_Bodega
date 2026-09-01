from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventario.models import Kardex, Stock

from .models import RecepcionDetalle


@receiver(post_save, sender=RecepcionDetalle)
def registrar_entrada_kardex(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():
        stock, _ = Stock.objects.select_for_update().get_or_create(
            producto=instance.producto,
            ubicacion=instance.ubicacion,
            lote=instance.lote,
            defaults={'fecha_vencimiento': instance.fecha_vencimiento, 'cantidad': 0},
        )
        stock_anterior = stock.cantidad
        stock.cantidad += instance.cantidad
        if instance.fecha_vencimiento:
            stock.fecha_vencimiento = instance.fecha_vencimiento
        stock.save()

        Kardex.objects.create(
            tipo=Kardex.ENTRADA,
            producto=instance.producto,
            ubicacion=instance.ubicacion,
            cantidad=instance.cantidad,
            stock_anterior=stock_anterior,
            stock_resultante=stock.cantidad,
            documento=f'Recepción #{instance.recepcion_id}',
            usuario=instance.recepcion.registrado_por,
        )
