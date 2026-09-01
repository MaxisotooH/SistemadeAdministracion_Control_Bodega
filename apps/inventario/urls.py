from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('stock/', views.stock_list, name='stock'),
    path('kardex/', views.kardex_list, name='kardex'),
]
