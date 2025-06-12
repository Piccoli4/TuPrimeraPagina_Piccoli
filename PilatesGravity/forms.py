from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Clase, Reserva
from datetime import datetime


class ReservaForm(forms.Form):
    """
    Formulario para crear una nueva reserva.
    Permite seleccionar tipo de clase, día y horario en campos separados.
    """
    tipo_clase = forms.ChoiceField(
        choices=[('', 'Selecciona el tipo de clase')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_clase'
        }),
        label="Tipo de Clase",
        error_messages={
            'required': 'Debes seleccionar un tipo de clase.',
            'invalid_choice': 'Selecciona un tipo de clase válido.'
        }
    )
    
    dia = forms.ChoiceField(
        choices=[('', 'Selecciona el día')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_dia'
        }),
        label="Día de la Semana",
        error_messages={
            'required': 'Debes seleccionar un día.',
            'invalid_choice': 'Selecciona un día válido.'
        }
    )
    
    horario = forms.ChoiceField(
        choices=[('', 'Selecciona el horario')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_horario'
        }),
        label="Horario",
        error_messages={
            'required': 'Debes seleccionar un horario.',
            'invalid_choice': 'Selecciona un horario válido.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Usuario actual
        super().__init__(*args, **kwargs)
        
        # Obtener tipos únicos de clases activas disponibles
        tipos_disponibles = Clase.objects.filter(
            activa=True
        ).values_list('tipo', flat=True).distinct().order_by('tipo')
        
        self.fields['tipo_clase'].choices = [('', 'Selecciona el tipo de clase')] + [
            (tipo, dict(Clase.TIPO_CLASES).get(tipo, tipo)) for tipo in tipos_disponibles
        ]
        
        # Obtener días únicos disponibles
        dias_disponibles = Clase.objects.filter(
            activa=True
        ).values_list('dia', flat=True).distinct()
        
        # Ordenar días según el orden de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dias_ordenados = sorted(
            set(dias_disponibles), 
            key=lambda x: orden_dias.index(x) if x in orden_dias else 999
        )
        
        self.fields['dia'].choices = [('', 'Selecciona el día')] + [
            (dia, dia) for dia in dias_ordenados
        ]
        
        # Obtener horarios únicos disponibles (se filtrarán dinámicamente via AJAX)
        horarios_disponibles = Clase.objects.filter(
            activa=True
        ).values_list('horario', flat=True).distinct().order_by('horario')
        
        self.fields['horario'].choices = [('', 'Selecciona el horario')] + [
            (horario.strftime('%H:%M'), horario.strftime('%H:%M')) 
            for horario in horarios_disponibles
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_clase = cleaned_data.get('tipo_clase')
        dia = cleaned_data.get('dia')
        horario_str = cleaned_data.get('horario')
        
        if not self.user:
            raise ValidationError('Usuario no autenticado.')
        
        if tipo_clase and dia and horario_str:
            try:
                # Convertir string de horario a time object
                horario_time = datetime.strptime(horario_str, '%H:%M').time()
                
                # Buscar la clase específica
                clase = Clase.objects.get(
                    tipo=tipo_clase, 
                    dia=dia, 
                    horario=horario_time,
                    activa=True
                )
                
                # Verificar si la clase tiene cupo disponible
                if clase.esta_completa():
                    raise ValidationError(
                        f'La clase de {clase.get_tipo_display()} los {dia} a las {horario_str} '
                        'está completa. Por favor selecciona otra opción.'
                    )
                
                # Verificar que el usuario no tenga ya una reserva activa para este día
                reserva_existente = Reserva.objects.filter(
                    usuario=self.user,
                    clase__dia=dia,
                    activa=True
                ).first()
                
                if reserva_existente:
                    raise ValidationError(
                        f'Ya tienes una reserva activa para los {dia} '
                        f'({reserva_existente.clase.get_tipo_display()} a las '
                        f'{reserva_existente.clase.horario.strftime("%H:%M")}). '
                        'Solo puedes tener una reserva por día.'
                    )
                
                # Verificar que el usuario no tenga ya una reserva para esta clase específica
                reserva_clase_existente = Reserva.objects.filter(
                    usuario=self.user,
                    clase=clase,
                    activa=True
                ).first()
                
                if reserva_clase_existente:
                    raise ValidationError(
                        f'Ya tienes una reserva activa para esta clase específica. '
                        'No puedes reservar la misma clase dos veces.'
                    )
                
                # Agregar la clase al cleaned_data para usar en la vista
                cleaned_data['clase'] = clase
                
            except Clase.DoesNotExist:
                raise ValidationError(
                    f'No existe una clase de {tipo_clase} los {dia} a las {horario_str} '
                    'o la clase no está activa. Por favor verifica tu selección.'
                )
            except ValueError:
                raise ValidationError('Formato de horario inválido.')
        
        return cleaned_data

class ModificarReservaForm(forms.Form):
    """
    Formulario para modificar una reserva existente.
    Permite cambiar a una nueva clase disponible.
    """
    nueva_clase = forms.ModelChoiceField(
        queryset=Clase.objects.none(),  # Se definirá en __init__
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Nueva Clase",
        empty_label="Selecciona una nueva clase",
        error_messages={
            'required': 'Debes seleccionar una nueva clase.',
            'invalid_choice': 'Selecciona una clase válida.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.reserva_actual = kwargs.pop('reserva_actual', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.reserva_actual and self.user:
            # Verificar que el usuario sea el dueño de la reserva
            if self.reserva_actual.usuario != self.user:
                # Si no es el dueño, no mostrar opciones
                self.fields['nueva_clase'].queryset = Clase.objects.none()
                return
            
            # Obtener clases disponibles excluyendo:
            # 1. La clase actual de la reserva
            # 2. Clases inactivas
            # 3. Clases completas
            # 4. Clases del mismo día si el usuario ya tiene otra reserva en ese día
            
            clases_base = Clase.objects.filter(
                activa=True
            ).exclude(
                id=self.reserva_actual.clase.id
            )
            
            # Filtrar clases que no estén completas
            clases_disponibles = []
            for clase in clases_base:
                # Verificar cupo disponible
                if clase.esta_completa():
                    continue
                
                # Verificar que no haya conflicto con otras reservas del usuario en el mismo día
                conflicto = Reserva.objects.filter(
                    usuario=self.user,
                    clase__dia=clase.dia,
                    activa=True
                ).exclude(
                    id=self.reserva_actual.id
                ).exists()
                
                if not conflicto:
                    clases_disponibles.append(clase.id)
            
            # Establecer el queryset con las clases disponibles
            self.fields['nueva_clase'].queryset = Clase.objects.filter(
                id__in=clases_disponibles
            ).order_by('tipo', 'dia', 'horario')
    
    def clean_nueva_clase(self):
        nueva_clase = self.cleaned_data.get('nueva_clase')
        
        if not nueva_clase:
            return nueva_clase
        
        # Verificar que la clase siga teniendo cupo disponible
        if nueva_clase.esta_completa():
            raise ValidationError(
                f'La clase de {nueva_clase.get_tipo_display()} los {nueva_clase.dia} '
                f'a las {nueva_clase.horario.strftime("%H:%M")} ya no tiene cupos disponibles. '
                'Por favor selecciona otra clase.'
            )
        
        # Verificar que no haya conflicto con otras reservas activas del usuario
        if self.user and self.reserva_actual:
            conflicto = Reserva.objects.filter(
                usuario=self.user,
                clase__dia=nueva_clase.dia,
                activa=True
            ).exclude(
                id=self.reserva_actual.id
            ).exists()
            
            if conflicto:
                raise ValidationError(
                    f'Ya tienes una reserva activa para los {nueva_clase.dia}. '
                    'Solo puedes tener una reserva por día.'
                )
        
        return nueva_clase

class EliminarReservaForm(forms.Form):
    """
    Formulario de confirmación para eliminar una reserva.
    Incluye un checkbox de confirmación para evitar eliminaciones accidentales.
    """
    confirmar_eliminacion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Confirmo que deseo cancelar mi reserva",
        error_messages={
            'required': 'Debes confirmar que deseas cancelar tu reserva.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.reserva = kwargs.pop('reserva', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.reserva:
            # Personalizar el label con información específica de la reserva
            self.fields['confirmar_eliminacion'].label = (
                f"Confirmo que deseo cancelar mi reserva para la clase de "
                f"{self.reserva.clase.get_tipo_display()} los "
                f"{self.reserva.clase.dia} a las "
                f"{self.reserva.clase.horario.strftime('%H:%M')}"
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar que el usuario sea el dueño de la reserva
        if self.reserva and self.user:
            if self.reserva.usuario != self.user:
                raise ValidationError('No tienes permisos para cancelar esta reserva.')
            
            # Verificar que la reserva siga activa
            if not self.reserva.activa:
                raise ValidationError('Esta reserva ya está cancelada.')
            
            # Verificar restricciones de tiempo (12 horas de anticipación)
            puede_modificar, mensaje = self.reserva.puede_modificarse()
            if not puede_modificar:
                raise ValidationError(f'No puedes cancelar esta reserva: {mensaje}')
        
        return cleaned_data

class BuscarReservaForm(forms.Form):
    """
    Formulario para que los usuarios busquen sus reservas.
    Solo requiere el nombre de usuario para la búsqueda.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario'
        }),
        label="Nombre de Usuario",
        help_text="Ingresa tu nombre de usuario para ver tus reservas activas",
        error_messages={
            'required': 'Debes ingresar tu nombre de usuario.',
            'max_length': 'El nombre de usuario no puede exceder 150 caracteres.'
        }
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if username:
            # Verificar que el usuario existe
            try:
                user = User.objects.get(username=username)
                # Almacenar el usuario para uso posterior
                self.cleaned_data['user'] = user
            except User.DoesNotExist:
                raise ValidationError('No existe un usuario con ese nombre.')
        
        return username