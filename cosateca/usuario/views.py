from django.shortcuts import render, redirect
from .forms import RegistroForm, InicioSesionForm, CuestionarioForm, editarPerfilForm
from django.contrib import messages
from .models import Usuario, Preferencia, Gestor, Amonestacion
from objeto.models import Objeto, ListaDeseos
from almacen.models import Almacen
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value, Avg
from objeto.views import objetos_recomendados
from core.decorators import usuario_required, gestor_required, acceso_desde_login_requerido



# Create your views here.


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            sexo = form.cleaned_data['sexo']
            correo_electronico = form.cleaned_data['correo_electronico']
            telefono = form.cleaned_data['telefono']
            dni = form.cleaned_data['dni']
            nombre_usuario = form.cleaned_data['nombre_usuario']
            contraseña = form.cleaned_data['contraseña']

            
            
            nuevo_usuario = Usuario(
                first_name = nombre,
                last_name = apellido,
                fecha_nacimiento = fecha_nacimiento,
                sexo = sexo,
                email = correo_electronico,
                telefono =  telefono,
                dni = dni,
                username = nombre_usuario,
            )
            
            nuevo_usuario.set_password(contraseña)
            nuevo_usuario.save()
            request.session['usuario_id'] = nuevo_usuario.id
            
            return redirect('cuestionario_preferencias')
            
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})



def inicio_sesion(request):
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data['nombre_usuario']
            contraseña = form.cleaned_data['contraseña']
            usuario_autenticado = authenticate(request, username=nombre_usuario, password=contraseña)

            if(usuario_autenticado is not None and usuario_autenticado.is_staff):
                login(request, usuario_autenticado)
                return redirect('gestion_usuarios_administrador')
            
            elif usuario_autenticado is not None and not hasattr(usuario_autenticado, 'gestor'):
                try:
                    usuario_autenticado.preferencia
                    login(request, usuario_autenticado)
                    return redirect('menu')
                except Preferencia.DoesNotExist:
                    request.session['usuario_id'] = usuario_autenticado.id
                    return redirect('cuestionario_preferencias')
            elif(usuario_autenticado is not None and hasattr(usuario_autenticado, 'gestor')):
                login(request, usuario_autenticado)
                return redirect('gestion_reserva_gestor')
            
            

    else:
        form = InicioSesionForm()

    return render(request, 'inicio_sesion.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

def cuestionario_preferencias(request):
    usuario_id = request.session.get('usuario_id')
    print(usuario_id)

    if not usuario_id:
        # Si no se accede desde login, redirigir
        return redirect('home')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return redirect('home')

    # Evitar que el usuario complete el cuestionario 2 veces
    if hasattr(usuario, 'preferencia'):
        return redirect('menu')
    if request.method == 'POST':
        form = CuestionarioForm(request.POST)
        if form.is_valid():
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                usuario = Usuario.objects.get(id=usuario_id)
                tarea_tipo = form.cleaned_data['tarea_tipo']
                frecuencia_uso = form.cleaned_data['frecuencia_uso']
                experiencia = form.cleaned_data['experiencia']
                franja_horaria = form.cleaned_data['franja_horaria']
                nueva_preferencia = Preferencia(
                    tarea_tipo=tarea_tipo,
                    frecuencia_uso=frecuencia_uso,
                    experiencia=experiencia,
                    franja_horaria=franja_horaria,
                    usuario=usuario
                )
                nueva_preferencia.save()
                login(request, usuario)
                request.session.pop('usuario_id', None)
                return redirect('menu')

    else:
        form = CuestionarioForm()

    return render(request, 'cuestionario_preferencias.html', {'form': form})
    

@usuario_required
def menu(request):
    objetos = Objeto.objects.all()
    objetos_mejor_valorados = objetos.order_by('valoraciones_recibidas_objeto__estrellas')
    objetos_preferentes = objetos_recomendados(request)
    return render(request, 'menu.html', {'objetos_mejor_valorados': objetos_mejor_valorados, 'objetos_preferentes': objetos_preferentes})




@usuario_required
def lista_deseos(request):

    usuario = request.user
    listas_deseos = usuario.listas_deseos.all()

    objetos_deseados = [lista.objeto for lista in listas_deseos]

    return render(request, 'lista_deseos.html', {'usuario': usuario, 'objetos_deseados':objetos_deseados})


@usuario_required
def eliminar_objeto_lista_deseos(request, objeto_id):
    usuario = request.user
    objeto = Objeto.objects.get(id=objeto_id)
    entrada = ListaDeseos.objects.filter(usuario=usuario, objeto=objeto).first()
    
    if entrada in usuario.listas_deseos.all():
        entrada.delete()
        messages.success(request, 'Objeto eliminado de la lista de deseos.')
    else:
        messages.error(request, 'El objeto no está en tu lista de deseos.')

    return redirect('lista_deseos')
    


@login_required
def detalles_usuario(request):
    usuario = request.user

    if request.user.is_staff:
        return redirect('home')


    if request.method == 'POST':
        form = editarPerfilForm(request.POST, usuario=request.user)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            sexo = form.cleaned_data['sexo']
            correo_electronico = form.cleaned_data['correo_electronico']
            telefono = form.cleaned_data['telefono']
            dni = form.cleaned_data['dni']
            nombre_usuario = form.cleaned_data['nombre_usuario']

            
            
            
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.fecha_nacimiento = fecha_nacimiento
            usuario.sexo = sexo
            usuario.email = correo_electronico
            usuario.telefono =  telefono
            usuario.dni = dni
            usuario.username = nombre_usuario
        
            
            usuario.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuario')
            
    else:
        form = editarPerfilForm(initial={
            'nombre': usuario.first_name,
            'apellido': usuario.last_name,
            'fecha_nacimiento': usuario.fecha_nacimiento.strftime('%Y-%m-%d'),
            'sexo': usuario.sexo,
            'correo_electronico': usuario.email,
            'telefono': usuario.telefono,
            'dni': usuario.dni,
            'nombre_usuario': usuario.username,
        }, usuario=request.user)

    return render(request, 'detalles_usuario.html', {'usuario': usuario, 'form':form})



@usuario_required
def agregar_objeto_lista_deseos(request, objeto_id):
    usuario = request.user
    objeto = Objeto.objects.get(id=objeto_id)
    entrada = ListaDeseos.objects.filter(usuario=usuario, objeto=objeto).first()
    if entrada in usuario.listas_deseos.all():
        messages.error(request, 'El objeto ya está en tu lista de deseos.')
        return redirect('catalogo')
    elif not objeto:
        messages.error(request, 'El objeto no existe.')
        return redirect('catalogo')
    else:
        lista_deseos = ListaDeseos(usuario=usuario, objeto=objeto)
        lista_deseos.save()
        messages.success(request, 'Objeto agregado a la lista de deseos.')
        return redirect('catalogo')



@usuario_required
def consultar_huella_carbono_reducida(request):
    usuario = request.user
    alquileres_realizados = usuario.alquileres.filter(cancelada=False).all()
    total_objetos_alquilados = alquileres_realizados.count()

    objetos_alquilados = []
    for alquiler in alquileres_realizados:
        objeto = alquiler.objeto
        objetos_alquilados.append(objeto)

    tipo_cantidad = {cat[0]: 0 for cat in Objeto.ENUM_TAREA_TIPO}
    for obj in objetos_alquilados:
        tipo_cantidad[obj.categoria] += 1
    
    cantidad_huella_ahorrada = sum(obj.huella_carbono for obj in objetos_alquilados)

    huella_por_mes = { 
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0
    }
    for alquiler in alquileres_realizados:
        if alquiler.fecha_inicio:
            mes = alquiler.fecha_inicio.strftime('%B')
            huella = alquiler.objeto.huella_carbono
            huella_por_mes[mes] += huella


    arboles_plantados_estimados = cantidad_huella_ahorrada / 21  # Asumiendo que un árbol absorbe 21 kg de CO2 al año
    arboles_plantados_estimados = round(arboles_plantados_estimados, 2)    

    return render(request, 'huella_carbono_reducida.html',
                   {'n_obj_alquilados': total_objetos_alquilados,
                    'objetos_alquilados': objetos_alquilados,
                    'obj_tipo_cantidad': tipo_cantidad,
                    'cantidad_huella_ahorrada': cantidad_huella_ahorrada,
                    'huella_por_mes': huella_por_mes,
                    'arboles_plantados_estimados': arboles_plantados_estimados}
                    )


@usuario_required
def consultar_amonestaciones(request):
    usuario = request.user
    amonestaciones = usuario.amonestaciones_recibidas.all()

    total_amonestaciones = amonestaciones.filter(severidad='Grave').count() * 3 + amonestaciones.filter(severidad='Media').count() * 2 + amonestaciones.filter(severidad='Leve').count()
    
    return render(request, 'consultar_amonestaciones.html', {'amonestaciones': amonestaciones, 'total_amonestaciones': total_amonestaciones})



#------------------------------------------------------------------------------------------------------------------------------------

#Funcionalidades relacionadas con el gestor

#------------------------------------------------------------------------------------------------------------------------------------


@gestor_required
def amonestar_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        if request.method == 'POST':
            motivo = request.POST.get('motivo')
            severidad = request.POST.get('severidad')

            if motivo and severidad:
                amonestacion = Amonestacion.objects.create(
                    motivo=motivo,
                    severidad=severidad,
                    usuario=usuario,
                    gestor=request.user.gestor
                )
                messages.success(request, "Amonestación registrada exitosamente.")
            else:
                messages.error(request, "Por favor, completa todos los campos.")
        else:
            messages.error(request, "Método de solicitud no válido.")
        
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")

    return redirect('gestion_reserva_gestor')

#------------------------------------------------------------------------------------------------------------------------------------

#Funcionalidades relacionadas con el administrador

#------------------------------------------------------------------------------------------------------------------------------------

def gestion_usuarios_administrador(request):
    usuarios = Usuario.objects.all()
    
    return render(request, 'gestion_usuarios_administrador.html', {'usuarios': usuarios})