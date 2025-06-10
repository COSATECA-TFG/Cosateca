from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Almacen

@login_required
def obtener_almacenes(request):

    filtro = request.GET.get('busqueda_almacen', '')
    almacenes = Almacen.objects.all()
    if filtro:
        almacenes = almacenes.filter(nombre__icontains=filtro) | almacenes.filter(localizacion__ciudad__icontains=filtro)
    return render(request, 'almacenes.html', {'almacenes': almacenes,})