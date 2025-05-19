from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Clase, Turno
from .forms import ClienteForm, ClaseForm, TurnoForm, BusquedaTurnoForm

# Página de inicio
def home(request):
    return render(request, 'PilatesGravity/home.html')


# Crear cliente
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ClienteForm()
    return render(request, 'PilatesGravity/crear_cliente.html', {'form': form})


# Crear clase
def crear_clase(request):
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ClaseForm()
    return render(request, 'PilatesGravity/crear_clase.html', {'form': form})


# Crear turno
def crear_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TurnoForm()
    return render(request, 'PilatesGravity/crear_turno.html', {'form': form})


# Buscar turno por nombre de cliente
def buscar_turno(request):
    resultados = []
    if request.method == 'POST':
        form = BusquedaTurnoForm(request.POST)
        if form.is_valid():
            nombre_cliente = form.cleaned_data['nombre']
            resultados = Turno.objects.filter(cliente__nombre__icontains=nombre_cliente)
    else:
        form = BusquedaTurnoForm()
    return render(request, 'PilatesGravity/buscar_turno.html', {'form': form, 'resultados': resultados})

