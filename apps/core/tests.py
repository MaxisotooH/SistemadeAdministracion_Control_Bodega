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
