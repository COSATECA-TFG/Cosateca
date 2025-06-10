from django.shortcuts import render
from objeto.models import Objeto
from almacen.models import Almacen
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value, Avg

@login_required
def catalogo(request):
    herramientas = Objeto.objects.all()
    almacenes = Almacen.objects.all()
    categoria = request.GET.get('categoria', '')
    if categoria:
        herramientas = herramientas.filter(categoria__icontains=categoria)

    condicion = request.GET.get('condicion', '')
    if condicion:
        herramientas = herramientas.filter(condicion__icontains=condicion)

    localizacion = request.GET.get('almacen', '')
    if localizacion:
        herramientas = herramientas.filter(almacen__nombre__icontains=localizacion)

    orden_condicion = request.GET.get('orden_condicion', '')
    if orden_condicion: 
        herramientas = herramientas.annotate(
            condicion_valor=Case(
                When(condicion='Nuevo', then=Value(1)),
                When(condicion='Bueno', then=Value(2)),
                When(condicion='Desgastado', then=Value(3)),
                When(condicion='Perdido', then=Value(4)),
                default=0,
                output_field=IntegerField()
            )
        )
        if orden_condicion == 'Menor':
            herramientas = herramientas.order_by('-condicion_valor')
        else:
            herramientas = herramientas.order_by('condicion_valor')

    orden_valoracion = request.GET.get('orden_valoracion', '')
    if orden_valoracion:
        if orden_valoracion == 'Mayor':
            herramientas = herramientas.order_by('-valoraciones_recibidas_objeto__estrellas')
        else:
            herramientas = herramientas.order_by('valoraciones_recibidas_objeto__estrellas')
    if request.method == 'GET':
        nombre = request.GET.get('nombre_herramienta', '')
        if nombre:
            herramientas = herramientas.filter(nombre__icontains=nombre)
    return render(request, 'catalogo.html', {'herramientas': herramientas, 'almacenes':almacenes})



def detalle_objeto(request, objeto_id):
    objeto = Objeto.objects.get(id=objeto_id)

    estrellas = objeto.valoraciones_recibidas_objeto.aggregate(
        media_estrellas = Avg('estrellas')
    ) ['media_estrellas'] or 0






    return render(request, 'detalle_objeto.html', {'objeto': objeto, 'estrellas': estrellas})
        

