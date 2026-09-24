from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginLockoutTests(TestCase):
    """El login no debe 'romperse' con credenciales invalidas, y debe
    bloquear el acceso tras varios intentos fallidos (pedido explicito de
    negocio, y parte del documento funcional original: 'Bloqueo de acceso
    ante credenciales invalidas')."""

    def setUp(self):
        self.usuario = User.objects.create_user('demo', password='ClaveBuena123')

    def test_credenciales_invalidas_muestra_mensaje_no_rompe_la_pagina(self):
        response = self.client.post(reverse('login'), {
            'username': 'demo', 'password': 'clave-equivocada',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'usuario y clave correctos')

    def test_bloquea_tras_varios_intentos_fallidos(self):
        for _ in range(5):
            self.client.post(reverse('login'), {
                'username': 'demo', 'password': 'clave-equivocada',
            })

        response = self.client.post(reverse('login'), {
            'username': 'demo', 'password': 'ClaveBuena123',  # ¡la correcta!
        })
        # Bloqueado incluso con la clave correcta: eso es justamente el punto.
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Demasiados intentos fallidos', status_code=429)

    def test_login_correcto_antes_del_limite_funciona(self):
        for _ in range(3):
            self.client.post(reverse('login'), {
                'username': 'demo', 'password': 'clave-equivocada',
            })

        response = self.client.post(reverse('login'), {
            'username': 'demo', 'password': 'ClaveBuena123',
        })
        self.assertEqual(response.status_code, 302)


class PaginasDeErrorTests(TestCase):
    """Un usuario sin permiso ve una pantalla amigable, no el 403 plano de
    Django (encontrado durante la revision con el gerente)."""

    def setUp(self):
        self.usuario = User.objects.create_user('sinrol', password='ClaveBuena123')

    def test_403_usa_plantilla_propia(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('recepcion:nueva'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'No tienes permiso para ver esta página', status_code=403)


class AdminAxesEnEspanolTests(TestCase):
    """El admin de django-axes (Access attempts, etc.) no trae traduccion
    al español -- se reemplaza por un admin propio en apps/core/admin.py.
    Estas pruebas confirman que un administrador puede desbloquear a un
    usuario con un solo clic, en español, sin la accion generica
    "Eliminar" que trae Django por defecto (para no confundir)."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            'super_es', 'super@test.com', 'ClaveBuena123',
        )
        self.bloqueado = User.objects.create_user('bloqueado_demo', password='ClaveBuena123')
        for _ in range(5):
            self.client.post(reverse('login'), {
                'username': 'bloqueado_demo', 'password': 'clave-mala',
            })
        self.client.logout()

    def test_pantalla_de_intentos_esta_en_espanol(self):
        self.client.force_login(self.admin)
        response = self.client.get('/admin/axes/accessattempt/')
        self.assertContains(response, 'Intentos de acceso')
        self.assertNotContains(response, 'Access attempts')

    def test_solo_existe_la_accion_desbloquear_no_la_de_eliminar(self):
        self.client.force_login(self.admin)
        response = self.client.get('/admin/axes/accessattempt/')
        self.assertContains(response, 'Desbloquear usuario')
        self.assertNotContains(response, 'Eliminar Intentos de acceso')

    def test_desbloquear_desde_el_admin_deja_entrar_de_nuevo(self):
        from axes.models import AccessAttempt

        self.client.force_login(self.admin)
        intento = AccessAttempt.objects.get(username='bloqueado_demo')
        self.client.post('/admin/axes/accessattempt/', {
            'action': 'desbloquear_seleccionados',
            '_selected_action': [str(intento.pk)],
        })
        self.client.logout()

        response = self.client.post(reverse('login'), {
            'username': 'bloqueado_demo', 'password': 'ClaveBuena123',
        })
        self.assertEqual(response.status_code, 302)
