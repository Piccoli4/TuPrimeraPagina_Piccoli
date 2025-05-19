from django import forms
from .models import Cliente, Clase, Turno

# Formulario para crear un cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono']


# Formulario para crear una clase
class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre', 'dia', 'hora', 'cupo_maximo']


# Formulario para crear un turno
class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente', 'clase', 'fecha', 'confirmado']


# Formulario para buscar turnos por nombre de cliente
class BusquedaTurnoForm(forms.Form):
    nombre = forms.CharField(label='Nombre del cliente', max_length=100)
