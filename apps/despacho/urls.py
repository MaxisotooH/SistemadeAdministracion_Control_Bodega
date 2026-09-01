from django.urls import path

from . import views

app_name = 'despacho'

urlpatterns = [
    path('', views.despacho_list, name='lista'),
    path('nuevo/', views.despacho_create, name='nuevo'),
    path('<int:pk>/', views.despacho_detail, name='detalle'),
]
