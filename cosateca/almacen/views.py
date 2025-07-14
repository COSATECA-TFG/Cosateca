from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Almacen, AlmacenValoracion, AlmacenValoracionDenuncia
from django.db.models import Avg
from core.models import BaseValoracionDenuncia
from core.decorators import usuario_required, admin_required
from almacen.models import Horario, Almacen, Localizacion
from django.contrib import messages



@login_required
def obtener_almacenes(request):
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    usuario = request.user
    filtro = request.GET.get('busqueda_almacen', '')
    almacenes = Almacen.objects.all()
    if filtro:
        almacenes = almacenes.filter(nombre__icontains=filtro) | almacenes.filter(localizacion__ciudad__icontains=filtro)
    if usuario.is_staff:
        return render(request, 'gestion_almacen_administrador.html', {'almacenes': almacenes, 'dias_semana':dias_semana})
    else:
        return render(request, 'almacenes.html', {'almacenes': almacenes, 'usuario': usuario})

@usuario_required
def obtener_almacen(request, almacen_id):
    if almacen_id:
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            valoracion_existente = AlmacenValoracion.objects.filter(almacen=almacen, usuario=request.user).first()
            return render(request, 'almacen_valoracion.html', {'almacen': almacen, 'valoracion': valoracion_existente})
        except Almacen.DoesNotExist:
            return render(request, 'almacen_valoracion.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'almacen_valoracion.html', {'error': 'ID de almacén no proporcionado'})
    
@usuario_required
def obtener_comentarios(request, almacen_id):
    if almacen_id:
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            comentarios = almacen.valoraciones_recibidas_almacen.all()
            valoracion_media = comentarios.aggregate(Avg('estrellas'))['estrellas__avg']
            denuncia_choices = BaseValoracionDenuncia.ENUM_CATEGORIA_DENUNCIA

            # Añadir información de denuncia para cada comentario
            comentarios_info = []
            for comentario in comentarios:
                ya_denunciado = AlmacenValoracionDenuncia.objects.filter(
                    valoracion=comentario, usuario=request.user
                ).exists()
                comentarios_info.append({
                    'comentario': comentario,
                    'ya_denunciado': ya_denunciado
                })

            return render(request, 'comentarios_almacen.html', {
                'almacen': almacen,
                'comentarios_info': comentarios_info,
                'valoracion_media': valoracion_media,
                'denuncia_choices': denuncia_choices
})
        except Almacen.DoesNotExist:
            return render(request, 'comentarios_almacen.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'comentarios_almacen.html', {'error': 'ID de almacén no proporcionado'})
    
@usuario_required
def valorar_almacen(request, almacen_id):
    try:
        almacen = Almacen.objects.get(id=almacen_id)
        valoracion_existente = AlmacenValoracion.objects.filter(almacen=almacen, usuario=request.user).first()

        if request.method == 'POST':
            valoracion = request.POST.get('puntuacion')
            comentario = request.POST.get('comentario')

            if not valoracion or not comentario.strip():
                return render(request, 'almacen_valoracion.html', {
                    'almacen': almacen,
                    'valoracion': valoracion_existente,
                    'error': 'Debes proporcionar una puntuación y un comentario.'
                })

            if valoracion_existente:
                valoracion_existente.estrellas = valoracion
                valoracion_existente.comentario = comentario.strip()
                valoracion_existente.save()
            else:
                nueva_valoracion = AlmacenValoracion(
                    almacen=almacen,
                    usuario=request.user,
                    estrellas=valoracion,
                    comentario=comentario.strip()
                )
                nueva_valoracion.save()

            return redirect('comentarios', almacen_id=almacen_id)

        return render(request, 'almacen_valoracion.html', {
            'almacen': almacen,
            'valoracion': valoracion_existente
        })
    except Almacen.DoesNotExist:
        return render(request, 'almacenes.html', {'error': 'Almacén no encontrado'})

@usuario_required
def eliminar_valoracion_almacen(request, comentario_id):
    try:
        comentario = AlmacenValoracion.objects.get(id=comentario_id, usuario=request.user)
        almacen_id = comentario.almacen.id
        comentario.delete()
        return redirect('comentarios', almacen_id=almacen_id)
    except AlmacenValoracion.DoesNotExist:
        return redirect('menu')
@usuario_required
def denunciar_valoracion_almacen(request, comentario_id):
    try:
        comentario = AlmacenValoracion.objects.get(id=comentario_id)
        denuncia_existente = AlmacenValoracionDenuncia.objects.filter(valoracion=comentario, usuario=request.user).first()
        if denuncia_existente:
            denuncia_existente.categoria = request.POST.get('categoria', '')
            denuncia_existente.contexto = request.POST.get('contexto', '')
            denuncia_existente.save()
        else:
            nueva_denuncia = comentario.denuncias_recibidas_almacen.create(
                usuario=request.user,
                categoria=request.POST.get('categoria', ''),
                contexto= request.POST.get('contexto', '')
            )
            nueva_denuncia.save()
        return redirect('comentarios', almacen_id=comentario.almacen.id)
    except AlmacenValoracion.DoesNotExist:
        return render(request, 'comentarios_almacen.html', {'error': 'Comentario no encontrado o no autorizado'})
    

#------------------------------------------------------------------------------------------------------------------------------------

#Funcionalidades relacionadas con el administrador

#------------------------------------------------------------------------------------------------------------------------------------

@admin_required
def crear_almacen(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        latitud = request.POST.get('latitud')
        pais = request.POST.get('pais')
        longitud = request.POST.get('longitud')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero_calle')
        
        if not nombre or not descripcion or not latitud or not longitud or not pais or not ciudad or not codigo_postal or not calle or not numero:
            messages.error("Todos los campos son obligatorios.")
            return redirect('almacenes')
        
        try:
            latitud = float(latitud.replace(',', '.'))
            longitud = float(longitud.replace(',', '.'))
        except ValueError:
            messages.error("Latitud y longitud deben ser números válidos.")
            return redirect('almacenes')
        
        try:
            codigo_postal = int(codigo_postal)
        except ValueError:
            messages.error("El código postal debe ser un número entero.")
            return redirect('almacenes')
        

        nueva_localizacion = Localizacion.objects.create(
            latitud=latitud,
            longitud=longitud,
            pais=pais,
            ciudad=ciudad,
            codigo_postal=codigo_postal,
            calle=calle,
            numero=numero
        )

        nuevo_almacen = Almacen.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            localizacion=nueva_localizacion
        )



        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for dia in dias_semana:
            hora_inicio = request.POST.get(f'horario_{dia}_inicio')
            hora_fin = request.POST.get(f'horario_{dia}_fin')

            if hora_inicio and hora_fin:
                Horario.objects.create(
                    almacen=nuevo_almacen,
                    dia_semana=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )

        return redirect('almacenes')
    
@admin_required
def editar_almacen(request, almacen_id):
    almacen_editar = Almacen.objects.get(id=almacen_id)
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        pais = request.POST.get('pais')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero_calle')

        if not nombre or not descripcion or not latitud or not longitud or not pais or not ciudad or not codigo_postal or not calle or not numero:
            messages.error("Todos los campos son obligatorios.")
            return redirect('almacenes_administrador')

        try:
            latitud = float(latitud.replace(',', '.'))
            longitud = float(longitud.replace(',', '.'))
        except ValueError:
            messages.error("Latitud y longitud deben ser números válidos.")
            return redirect('almacenes_administrador')

        try:
            codigo_postal = int(codigo_postal)
        except ValueError:
            messages.error("El código postal debe ser un número entero.")
            return redirect('almacenes_administrador')

        almacen_editar.nombre = nombre
        almacen_editar.descripcion = descripcion
        almacen_editar.localizacion.latitud = latitud
        almacen_editar.localizacion.longitud = longitud
        almacen_editar.localizacion.pais = pais
        almacen_editar.localizacion.ciudad = ciudad
        almacen_editar.localizacion.codigo_postal = codigo_postal
        almacen_editar.localizacion.calle = calle
        almacen_editar.localizacion.numero = numero

        almacen_editar.localizacion.save()
        almacen_editar.save()

        for dia in dias_semana:
            hora_inicio = request.POST.get(f'horario_{dia}_inicio')
            hora_fin = request.POST.get(f'horario_{dia}_fin')
            if hora_inicio and hora_fin:

                Horario.objects.update_or_create(
                    almacen=almacen_editar,
                    dia_semana=dia,
                    defaults={'hora_inicio': hora_inicio, 'hora_fin': hora_fin}
                )

        return redirect('almacenes_administrador')
    
@admin_required
def eliminar_almacen(request, almacen_id):
    almacen_a_ekiminar = Almacen.objects.get(id=almacen_id)
    almacen_a_ekiminar.delete()
    messages.success(request, "Almacén eliminado correctamente.")
    return redirect('almacenes_administrador')





