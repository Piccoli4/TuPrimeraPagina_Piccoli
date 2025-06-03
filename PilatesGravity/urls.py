from django.urls import path
from .views import (
    home, reservar_clase, conoce_mas,
    dias_disponibles, horarios_disponibles, 
    verificar_disponibilidad, clases_disponibles_api
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('reservar_clase/', reservar_clase, name='reservar_clase'),
    path('conoce-mas/', conoce_mas, name='conoce_mas'),
    path('politica-de-privacidad/', TemplateView.as_view(template_name='PilatesGravity/politica_privacidad.html'), name='politica_privacidad'),
    path('terminos_condiciones/', TemplateView.as_view(template_name='PilatesGravity/terminos_condiciones.html'), name='terminos_condiciones'),

    # API endpoints para AJAX
    path('api/dias-disponibles/', dias_disponibles, name='dias_disponibles'),
    path('api/horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'),
    path('api/verificar-disponibilidad/', verificar_disponibilidad, name='verificar_disponibilidad'),
    path('api/clases-disponibles/', clases_disponibles_api, name='clases_disponibles_api'),
]