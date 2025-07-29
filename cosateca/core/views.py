from django.shortcuts import render

# Create your views here.


def home(request):
    """
    Render the home page of the application.
    """
    return render(request, 'home.html')


def leer_mas(request):
    """
    Render the home page of the application.
    """
    return render(request, 'leer_mas.html')