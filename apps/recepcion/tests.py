from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

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


class RecepcionPermisosTests(TestCase):
    """Un usuario sin el rol adecuado no debe poder crear ni ver recepciones."""

    def setUp(self):
        self.sin_rol = User.objects.create_user('sinrol', password='clave12345')

        self.consulta = User.objects.create_user('consulta', password='clave12345')
        self.consulta.groups.add(Group.objects.get(name='Contabilidad (consulta)'))

        self.operador = User.objects.create_user('operador2', password='clave12345')
        self.operador.groups.add(Group.objects.get(name='Operador de Bodega'))

    def test_usuario_sin_rol_no_puede_ver_ni_crear(self):
        self.client.force_login(self.sin_rol)
        self.assertEqual(self.client.get(reverse('recepcion:lista')).status_code, 403)
        self.assertEqual(self.client.get(reverse('recepcion:nueva')).status_code, 403)

    def test_rol_de_solo_consulta_puede_ver_pero_no_crear(self):
        self.client.force_login(self.consulta)
        self.assertEqual(self.client.get(reverse('recepcion:lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('recepcion:nueva')).status_code, 403)

    def test_operador_de_bodega_puede_crear(self):
        self.client.force_login(self.operador)
        self.assertEqual(self.client.get(reverse('recepcion:nueva')).status_code, 200)


class RecepcionPaginacionTests(TestCase):
    """Antes el listado cortaba en los ultimos 100 registros y no habia
    forma de ver los mas antiguos. Se confirma que con mas registros de
    los que caben en una pagina, se puede navegar a los siguientes."""

    def setUp(self):
        self.usuario = User.objects.create_user('operador3', password='clave12345')
        self.usuario.groups.add(Group.objects.get(name='Operador de Bodega'))
        proveedor = Proveedor.objects.create(razon_social='Proveedor paginacion', rut='3-5')
        for i in range(30):
            Recepcion.objects.create(
                proveedor=proveedor, fecha='2026-01-01', registrado_por=self.usuario,
            )

    def test_primera_pagina_muestra_25_y_hay_boton_siguiente(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('recepcion:lista'))
        self.assertEqual(len(response.context['recepciones']), 25)
        self.assertContains(response, 'Siguiente')

    def test_segunda_pagina_muestra_los_5_restantes(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('recepcion:lista'), {'pagina': 2})
        self.assertEqual(len(response.context['recepciones']), 5)
