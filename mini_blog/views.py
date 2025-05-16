from django.shortcuts import render, redirect, get_object_or_404
from .models import Autor, Categoria, Post
from .forms import AutorForm, CategoriaForm, PostForm, BusquedaPostForm

# Página de inicio
def home(request):
    return render(request, 'mini_blog/home.html')

# Crear un nuevo autor
def crear_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AutorForm()
    return render(request, 'mini_blog/crear_autor.html', {'form': form})

# Crear una nueva categoría
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoriaForm()
    return render(request, 'mini_blog/crear_categoria.html', {'form': form})

# Crear un nuevo post
def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'mini_blog/crear_post.html', {'form': form})

# Buscar un post por titulo
def buscar_post(request):
    if request.method == 'POST':
        form = BusquedaPostForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            posts = Post.objects.filter(titulo__icontains=titulo)
            return render(request, 'mini_blog/buscar_post.html', {'posts': posts})
    else:
        form = BusquedaPostForm()
    return render(request, 'mini_blog/buscar_post.html', {'form': form})

# Listar todos los autores
def listar_autores(request):
    autores = Autor.objects.all()
    contexto = {
        'autores': autores
    }
    return render(request, 'mini_blog/listar_autores.html', contexto)
