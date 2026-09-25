from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.pagination import paginar

from .forms import RecepcionDetalleFormSet, RecepcionForm
from .models import Recepcion


@login_required
@permission_required('recepcion.view_recepcion', raise_exception=True)
def recepcion_list(request):
    recepciones = Recepcion.objects.select_related('proveedor').order_by('-fecha', '-id')
    return render(request, 'recepcion/list.html', {'recepciones': paginar(request, recepciones)})


@login_required
@permission_required('recepcion.add_recepcion', raise_exception=True)
def recepcion_create(request):
    if request.method == 'POST':
        form = RecepcionForm(request.POST)
        formset = RecepcionDetalleFormSet(request.POST, prefix='detalles')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                recepcion = form.save(commit=False)
                recepcion.registrado_por = request.user
                recepcion.save()
                formset.instance = recepcion
                formset.save()
            messages.success(request, f'Recepción #{recepcion.pk} registrada correctamente.')
            return redirect('recepcion:detalle', pk=recepcion.pk)
    else:
        form = RecepcionForm()
        formset = RecepcionDetalleFormSet(prefix='detalles')
    return render(request, 'recepcion/form.html', {'form': form, 'formset': formset})


@login_required
@permission_required('recepcion.view_recepcion', raise_exception=True)
def recepcion_detail(request, pk):
    recepcion = get_object_or_404(
        Recepcion.objects.select_related('proveedor', 'registrado_por')
        .prefetch_related('detalles__producto', 'detalles__ubicacion'),
        pk=pk,
    )
    return render(request, 'recepcion/detail.html', {'recepcion': recepcion})
