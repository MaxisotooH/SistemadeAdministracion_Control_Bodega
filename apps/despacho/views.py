from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DespachoDetalleFormSet, DespachoForm
from .models import Despacho


@login_required
def despacho_list(request):
    despachos = Despacho.objects.select_related('cliente').order_by('-fecha', '-id')[:100]
    return render(request, 'despacho/list.html', {'despachos': despachos})


@login_required
def despacho_create(request):
    if request.method == 'POST':
        form = DespachoForm(request.POST)
        formset = DespachoDetalleFormSet(request.POST, prefix='detalles')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                despacho = form.save(commit=False)
                despacho.registrado_por = request.user
                despacho.save()
                formset.instance = despacho
                formset.save()
            messages.success(request, f'Despacho #{despacho.pk} registrado correctamente.')
            return redirect('despacho:detalle', pk=despacho.pk)
    else:
        form = DespachoForm()
        formset = DespachoDetalleFormSet(prefix='detalles')
    return render(request, 'despacho/form.html', {'form': form, 'formset': formset})


@login_required
def despacho_detail(request, pk):
    despacho = get_object_or_404(
        Despacho.objects.select_related('cliente', 'registrado_por')
        .prefetch_related('detalles__producto', 'detalles__ubicacion'),
        pk=pk,
    )
    return render(request, 'despacho/detail.html', {'despacho': despacho})
