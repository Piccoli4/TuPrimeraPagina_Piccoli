from django.urls import path
from .views import home, crear_cliente, crear_clase, crear_turno, buscar_turno
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('crear_cliente/', crear_cliente, name='crear_cliente'),
    path('crear_clase/', crear_clase, name='crear_clase'),
    path('crear_turno/', crear_turno, name='crear_turno'),
    path('buscar_turno/', buscar_turno, name='buscar_turno'),
    path('politica-de-privacidad/', TemplateView.as_view(template_name='PilatesGravity/politica_privacidad.html'), name='politica_privacidad'),
]