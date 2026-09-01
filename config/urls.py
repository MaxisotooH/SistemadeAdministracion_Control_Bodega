"""Enrutamiento raíz del proyecto."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    # A medida que se desarrolle cada módulo, se agrega aquí su
    # namespace, por ejemplo:
    # path('maestros/', include('apps.maestros.urls')),
    # path('compras/', include('apps.compras.urls')),
    # path('recepcion/', include('apps.recepcion.urls')),
    # path('despacho/', include('apps.despacho.urls')),
]
