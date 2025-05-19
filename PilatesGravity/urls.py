from django.urls import path
from .views import home, crear_cliente, crear_clase, crear_turno, buscar_turno

urlpatterns = [
    path('', home, name='home'),
    path('crear_cliente/', crear_cliente, name='crear_cliente'),
    path('crear_clase/', crear_clase, name='crear_clase'),
    path('crear_turno/', crear_turno, name='crear_turno'),
    path('buscar_turno/', buscar_turno, name='buscar_turno'),
]