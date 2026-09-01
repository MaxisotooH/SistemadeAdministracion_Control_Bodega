from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.inventario.models import Kardex, Stock
from apps.maestros.models import Bodega, Categoria, Cliente, Producto, UnidadMedida, Ubicacion, Zona

from .forms import DespachoDetalleFormSet
from .models import Despacho, DespachoDetalle

User = get_user_model()


class DespachoStockTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('operador', password='clave12345')
        categoria = Categoria.objects.create(nombre='General')
        unidad = UnidadMedida.objects.create(codigo='UN', nombre='Unidad')
        self.producto = Producto.objects.create(
            sku='SKU-1', nombre='Producto test', categoria=categoria, unidad_medida=unidad,
        )
        bodega = Bodega.objects.create(codigo='B1', nombre='Bodega 1')
        zona = Zona.objects.create(bodega=bodega, codigo='Z1', nombre='Zona 1')
        self.ubicacion = Ubicacion.objects.create(zona=zona, codigo='U1')
        self.cliente = Cliente.objects.create(razon_social='Cliente test', rut='1-9')
        Stock.objects.create(producto=self.producto, ubicacion=self.ubicacion, cantidad=30)

    def _crear_despacho(self):
        return Despacho.objects.create(
            cliente=self.cliente, fecha='2026-01-01', registrado_por=self.usuario,
        )

    def test_despacho_descuenta_stock_y_registra_kardex_salida(self):
        despacho = self._crear_despacho()
        DespachoDetalle.objects.create(
            despacho=despacho, producto=self.producto, ubicacion=self.ubicacion, cantidad=20,
        )

        stock = Stock.objects.get(producto=self.producto, ubicacion=self.ubicacion, lote='')
        self.assertEqual(stock.cantidad, 10)

        movimiento = Kardex.objects.get(producto=self.producto)
        self.assertEqual(movimiento.tipo, Kardex.SALIDA)
        self.assertEqual(movimiento.stock_anterior, 30)
        self.assertEqual(movimiento.stock_resultante, 10)
        self.assertEqual(movimiento.documento, f'Despacho #{despacho.pk}')

    def test_detalle_rechaza_cantidad_mayor_a_disponible(self):
        despacho = self._crear_despacho()
        detalle = DespachoDetalle(
            despacho=despacho, producto=self.producto, ubicacion=self.ubicacion, cantidad=1000,
        )
        with self.assertRaises(ValidationError):
            detalle.clean()

        # El stock no debe verse afectado por un intento invalido.
        stock = Stock.objects.get(producto=self.producto, ubicacion=self.ubicacion, lote='')
        self.assertEqual(stock.cantidad, 30)

    def test_formset_rechaza_lineas_que_juntas_superan_el_stock(self):
        despacho = self._crear_despacho()
        data = {
            'detalles-TOTAL_FORMS': '2',
            'detalles-INITIAL_FORMS': '0',
            'detalles-MIN_NUM_FORMS': '0',
            'detalles-MAX_NUM_FORMS': '1000',
            'detalles-0-producto': self.producto.pk,
            'detalles-0-ubicacion': self.ubicacion.pk,
            'detalles-0-cantidad': '20',
            'detalles-0-lote': '',
            'detalles-1-producto': self.producto.pk,
            'detalles-1-ubicacion': self.ubicacion.pk,
            'detalles-1-cantidad': '20',
            'detalles-1-lote': '',
        }
        formset = DespachoDetalleFormSet(data, instance=despacho, prefix='detalles')

        self.assertFalse(formset.is_valid())
        self.assertIn('disponible 30', str(formset.non_form_errors()))

        stock = Stock.objects.get(producto=self.producto, ubicacion=self.ubicacion, lote='')
        self.assertEqual(stock.cantidad, 30)
