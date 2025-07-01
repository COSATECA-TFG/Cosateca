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
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            Gestor.objects.get(usuario_ptr=request.user)
            messages.error(request, "Los gestores no tienen acceso a esta funcionalidad.")
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
            return redirect('login')
        
        try:
            Gestor.objects.get(usuario_ptr=request.user)
            return view_func(request, *args, **kwargs)
        except Gestor.DoesNotExist:
            messages.error(request, "Esta funcionalidad está reservada para gestores.")
            return redirect('home')  
    
    return wrapper
