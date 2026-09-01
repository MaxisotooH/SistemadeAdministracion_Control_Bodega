from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """Panel principal. Se irá completando con indicadores por módulo
    (stock crítico, recepciones pendientes, despachos del día, etc.)."""
    return render(request, 'core/dashboard.html')
