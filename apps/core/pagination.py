from django.core.paginator import Paginator


def paginar(request, queryset, por_pagina=25):
    """Pagina un queryset segun el parametro ?pagina= de la URL.

    get_page() ya maneja numeros de pagina invalidos o fuera de rango
    (los ajusta a la primera/ultima pagina en vez de lanzar un error).
    """
    paginator = Paginator(queryset, por_pagina)
    return paginator.get_page(request.GET.get('pagina'))
