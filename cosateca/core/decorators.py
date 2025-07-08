from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from usuario.models import Gestor

def usuario_required(view_func):
    """
    Decorador que requiere que el usuario esté logueado y NO sea un gestor.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_staff:
            return redirect('home')
        
        try:
            Gestor.objects.get(usuario_ptr=request.user)
            return redirect('home')  
        except Gestor.DoesNotExist:
            return view_func(request, *args, **kwargs)
    
    return wrapper

def gestor_required(view_func):
    """
    Decorador que requiere que el usuario sea un gestor.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        
        try:
            Gestor.objects.get(usuario_ptr=request.user)
            return view_func(request, *args, **kwargs)
        except Gestor.DoesNotExist:
            return redirect('home')  
    
    return wrapper

from django.shortcuts import redirect
from functools import wraps

def acceso_desde_login_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('inicio_sesion')  # nombre de tu URL de login
        return view_func(request, *args, **kwargs)
    return _wrapped_view

