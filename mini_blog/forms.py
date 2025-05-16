from django import forms
from .models import Autor, Categoria, Post

# Formulario para crear autores
class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre', 'apellido', 'email', 'biografia']


# Formulario para crear categorías
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


# Formulario para crear posts
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'autor', 'categoria']


# Formulario para buscar posts por título
class BusquedaPostForm(forms.Form):
    titulo = forms.CharField(label='Buscar por título', max_length=100)
