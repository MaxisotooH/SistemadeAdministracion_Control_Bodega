from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.inventario.models import Kardex, Stock
from apps.maestros.models import Bodega, Categoria, Producto, Proveedor, UnidadMedida, Ubicacion, Zona

from .models import Recepcion, RecepcionDetalle

User = get_user_model()


class RecepcionKardexTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('operador', password='clave12345')
        self.categoria = Categoria.objects.create(nombre='General')
        self.unidad = UnidadMedida.objects.create(codigo='UN', nombre='Unidad')
        self.producto = Producto.objects.create(
            sku='SKU-1', nombre='Producto test',
            categoria=self.categoria, unidad_medida=self.unidad,
        )
        bodega = Bodega.objects.create(codigo='B1', nombre='Bodega 1')
        zona = Zona.objects.create(bodega=bodega, codigo='Z1', nombre='Zona 1')
        self.ubicacion = Ubicacion.objects.create(zona=zona, codigo='U1')
        self.proveedor = Proveedor.objects.create(razon_social='Proveedor test', rut='1-9')

    def test_recepcion_crea_stock_y_kardex_entrada(self):
        recepcion = Recepcion.objects.create(
            proveedor=self.proveedor, fecha='2026-01-01', registrado_por=self.usuario,
        )
        RecepcionDetalle.objects.create(
            recepcion=recepcion, producto=self.producto, ubicacion=self.ubicacion, cantidad=30,
        )

        stock = Stock.objects.get(producto=self.producto, ubicacion=self.ubicacion, lote='')
        self.assertEqual(stock.cantidad, 30)

        movimiento = Kardex.objects.get(producto=self.producto)
        self.assertEqual(movimiento.tipo, Kardex.ENTRADA)
        self.assertEqual(movimiento.cantidad, 30)
        self.assertEqual(movimiento.stock_anterior, 0)
        self.assertEqual(movimiento.stock_resultante, 30)
        self.assertEqual(movimiento.documento, f'Recepción #{recepcion.pk}')

    def test_dos_recepciones_acumulan_stock(self):
        recepcion = Recepcion.objects.create(
            proveedor=self.proveedor, fecha='2026-01-01', registrado_por=self.usuario,
        )
        RecepcionDetalle.objects.create(
            recepcion=recepcion, producto=self.producto, ubicacion=self.ubicacion, cantidad=10,
        )
        RecepcionDetalle.objects.create(
            recepcion=recepcion, producto=self.producto, ubicacion=self.ubicacion, cantidad=5,
        )

        stock = Stock.objects.get(producto=self.producto, ubicacion=self.ubicacion, lote='')
        self.assertEqual(stock.cantidad, 15)
        self.assertEqual(Kardex.objects.filter(producto=self.producto).count(), 2)
