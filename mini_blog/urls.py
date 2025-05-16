from django.urls import path
from .views import (
    home,
    crear_autor,
    crear_categoria,
    crear_post,
    buscar_post,
    listar_autores,
)

urlpatterns = [
    path('', home, name='home'),
    path('crear_autor/', crear_autor, name='crear_autor'),
    path('crear_categoria/', crear_categoria, name='crear_categoria'),
    path('crear_post/', crear_post, name='crear_post'),
    path('buscar_post/', buscar_post, name='buscar_post'),
    path('listar-autores/', listar_autores, name='listar_autores'),
]