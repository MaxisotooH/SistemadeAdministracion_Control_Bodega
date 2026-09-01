from django.urls import path

from . import views

app_name = 'recepcion'

urlpatterns = [
    path('', views.recepcion_list, name='lista'),
    path('nueva/', views.recepcion_create, name='nueva'),
    path('<int:pk>/', views.recepcion_detail, name='detalle'),
]
