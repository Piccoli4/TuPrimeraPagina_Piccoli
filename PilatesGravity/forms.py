from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, Reserva, Clase

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'codigo_verificacion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu nombre',
                'maxlength': 100
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingresa tu apellido',
                'maxlength': 100
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com (opcional)'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono',
                'maxlength': 20
            }),
            'codigo_verificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000',
                'maxlength': 4,
                'pattern': '[0-9]{4}',
                'title': 'Debe ser exactamente 4 dígitos'
            })
        }

class ReservaForm(forms.Form):
    tipo_clase = forms.ChoiceField(
        choices=[('', 'Selecciona el tipo de clase')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_clase'
        }),
        label="Tipo de Clase"
    )
    
    dia = forms.ChoiceField(
        choices=[('', 'Selecciona el día')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_dia'
        }),
        label="Día de la Semana"
    )
    
    horario = forms.ChoiceField(
        choices=[('', 'Selecciona el horario')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_horario'
        }),
        label="Horario"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener tipos únicos de clases disponibles
        tipos_disponibles = Clase.objects.values_list('tipo', flat=True).distinct().order_by('tipo')
        self.fields['tipo_clase'].choices = [('', 'Selecciona el tipo de clase')] + [
            (tipo, dict(Clase.TIPO_CLASES).get(tipo, tipo)) for tipo in tipos_disponibles
        ]
        
        # Obtener días únicos disponibles - CORREGIDO para eliminar duplicados
        dias_disponibles = Clase.objects.values_list('dia', flat=True).distinct()
        # Ordenar días según el orden de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dias_ordenados = sorted(set(dias_disponibles), key=lambda x: orden_dias.index(x) if x in orden_dias else 999)
        
        self.fields['dia'].choices = [('', 'Selecciona el día')] + [
            (dia, dia) for dia in dias_ordenados
        ]
        
        # Obtener horarios únicos disponibles (se filtrarán dinámicamente)
        horarios_disponibles = Clase.objects.values_list('horario', flat=True).distinct().order_by('horario')
        self.fields['horario'].choices = [('', 'Selecciona el horario')] + [
            (horario.strftime('%H:%M'), horario.strftime('%H:%M')) for horario in horarios_disponibles
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_clase = cleaned_data.get('tipo_clase')
        dia = cleaned_data.get('dia')
        horario_str = cleaned_data.get('horario')
        
        if tipo_clase and dia and horario_str:
            try:
                from datetime import datetime
                horario_time = datetime.strptime(horario_str, '%H:%M').time()
                
                # Buscar la clase específica
                clase = Clase.objects.get(tipo=tipo_clase, dia=dia, horario=horario_time)
                
                # Verificar si la clase tiene cupo disponible
                if clase.esta_completa():
                    raise ValidationError(
                        f'La clase de {clase.get_tipo_display()} los {dia} a las {horario_str} '
                        'está completa. Por favor selecciona otra opción.'
                    )
                
                # Agregar la clase al cleaned_data para usar en la vista
                cleaned_data['clase'] = clase
                
            except Clase.DoesNotExist:
                raise ValidationError(
                    f'No existe una clase de {tipo_clase} los {dia} a las {horario_str}. '
                    'Por favor verifica tu selección.'
                )
        
        return cleaned_data

class BuscarReservaForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del cliente'
        }),
        label="Nombre"
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido del cliente'
        }),
        label="Apellido"
    )

class ConfirmarReservaForm(forms.Form):
    codigo_verificacion = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0000',
            'pattern': '[0-9]{4}',
            'maxlength': 4
        }),
        label="Código de Verificación"
    )
    
    def clean_codigo_verificacion(self):
        codigo = self.cleaned_data.get('codigo_verificacion')
        if not codigo.isdigit():
            raise ValidationError('El código debe contener solo números.')
        if len(codigo) != 4:
            raise ValidationError('El código debe tener exactamente 4 dígitos.')
        return codigo

class CambiarReservaForm(forms.Form):
    nueva_clase = forms.ModelChoiceField(
        queryset=Clase.objects.none(),  # Se definirá en __init__
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Nueva Clase",
        empty_label="Selecciona una nueva clase"
    )
    
    def __init__(self, *args, **kwargs):
        reserva_actual = kwargs.pop('reserva_actual', None)
        super().__init__(*args, **kwargs)
        
        if reserva_actual:
            # Mostrar todas las clases disponibles excepto la actual
            # y que tengan cupo disponible
            clases_disponibles = Clase.objects.exclude(
                id=reserva_actual.clase.id
            ).filter(
                # Solo mostrar clases que no estén completas
            ).order_by('tipo', 'dia', 'horario')
            
            # Filtrar manualmente las que tienen cupo
            clases_con_cupo = []
            for clase in clases_disponibles:
                if not clase.esta_completa():
                    clases_con_cupo.append(clase)
            
            self.fields['nueva_clase'].queryset = Clase.objects.filter(
                id__in=[clase.id for clase in clases_con_cupo]
            ).order_by('tipo', 'dia', 'horario')
    
    def clean_nueva_clase(self):
        nueva_clase = self.cleaned_data.get('nueva_clase')
        if nueva_clase and nueva_clase.esta_completa():
            raise ValidationError(
                f'La clase de {nueva_clase.tipo} los {nueva_clase.dia} '
                f'a las {nueva_clase.horario.strftime("%H:%M")} está completa. '
                'Por favor selecciona otra clase.'
            )
        return nueva_clase