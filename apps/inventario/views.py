from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from apps.core.pagination import paginar
from apps.maestros.models import Bodega, Producto

from .models import Kardex, Stock


@login_required
@permission_required('inventario.view_stock', raise_exception=True)
def stock_list(request):
    stocks = Stock.objects.select_related('producto', 'ubicacion__zona__bodega').filter(cantidad__gt=0)

    producto_id = request.GET.get('producto')
    bodega_id = request.GET.get('bodega')

    if producto_id:
        stocks = stocks.filter(producto_id=producto_id)
    if bodega_id:
        stocks = stocks.filter(ubicacion__zona__bodega_id=bodega_id)

    stocks = stocks.order_by('producto__nombre', 'ubicacion')

    filtros = request.GET.copy()
    filtros.pop('pagina', None)

    context = {
        'stocks': paginar(request, stocks),
        'productos': Producto.objects.filter(activo=True).order_by('nombre'),
        'bodegas': Bodega.objects.filter(activa=True).order_by('nombre'),
        'producto_id': producto_id,
        'bodega_id': bodega_id,
        'extra_qs': filtros.urlencode(),
    }
    return render(request, 'inventario/stock_list.html', context)


@login_required
@permission_required('inventario.view_kardex', raise_exception=True)
def kardex_list(request):
    movimientos = Kardex.objects.select_related('producto', 'ubicacion__zona__bodega', 'usuario')

    producto_id = request.GET.get('producto')
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)

    movimientos = movimientos.order_by('-creado_en')

    filtros = request.GET.copy()
    filtros.pop('pagina', None)

    context = {
        'movimientos': paginar(request, movimientos),
        'productos': Producto.objects.filter(activo=True).order_by('nombre'),
        'producto_id': producto_id,
        'extra_qs': filtros.urlencode(),
    }
    return render(request, 'inventario/kardex_list.html', context)
