from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from apps.inventario.models import Stock
from apps.recepcion.models import Recepcion, RecepcionDetalle

from .models import Bodega, Categoria, Producto, Proveedor, UnidadMedida, Ubicacion, Zona

User = get_user_model()


class MaestrosIntegridadTests(TestCase):
    """Un producto con movimientos no se puede borrar por accidente: la FK es
    PROTECT, asi que Django rechaza el borrado en vez de dejar Stock/Kardex
    apuntando a un producto inexistente."""

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
        proveedor = Proveedor.objects.create(razon_social='Proveedor test', rut='1-9')

        recepcion = Recepcion.objects.create(
            proveedor=proveedor, fecha='2026-01-01', registrado_por=self.usuario,
        )
        RecepcionDetalle.objects.create(
            recepcion=recepcion, producto=self.producto, ubicacion=self.ubicacion, cantidad=10,
        )

    def test_no_se_puede_borrar_producto_con_stock_o_kardex(self):
        with self.assertRaises(ProtectedError):
            self.producto.delete()

        # sigue existiendo intacto
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())
        self.assertEqual(Stock.objects.get(producto=self.producto).cantidad, 10)

    def test_producto_sin_movimientos_si_se_puede_borrar(self):
        otro = Producto.objects.create(
            sku='SKU-2', nombre='Producto sin uso',
            categoria=self.categoria, unidad_medida=self.unidad,
        )
        otro.delete()
        self.assertFalse(Producto.objects.filter(sku='SKU-2').exists())


class MaestrosPermisosAdminTests(TestCase):
    """Un rol de solo consulta (p.ej. Ventas) puede ver el admin de Maestros
    pero no puede agregar ni modificar productos."""

    def setUp(self):
        self.ventas = User.objects.create_user('ventas', password='clave12345', is_staff=True)
        self.ventas.groups.add(Group.objects.get(name='Ventas'))

        self.jefe = User.objects.create_user('jefe', password='clave12345', is_staff=True)
        self.jefe.groups.add(Group.objects.get(name='Jefe de Bodega'))

    def test_ventas_no_puede_agregar_producto_por_admin(self):
        self.client.force_login(self.ventas)
        response = self.client.get(reverse('admin:maestros_producto_add'))
        self.assertEqual(response.status_code, 403)

    def test_ventas_si_puede_ver_listado_de_productos(self):
        self.client.force_login(self.ventas)
        response = self.client.get(reverse('admin:maestros_producto_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_jefe_de_bodega_si_puede_agregar_producto_por_admin(self):
        self.client.force_login(self.jefe)
        response = self.client.get(reverse('admin:maestros_producto_add'))
        self.assertEqual(response.status_code, 200)
