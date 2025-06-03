from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime, timedelta

DIAS_SEMANA = [
    ('Lunes', 'Lunes'),
    ('Martes', 'Martes'),
    ('Miércoles', 'Miércoles'),
    ('Jueves', 'Jueves'),
    ('Viernes', 'Viernes'),
]

class Cliente(models.Model):
    numero_cliente = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.',
        }
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name="Apellido",
        error_messages={
            'required': 'El apellido es obligatorio.',
            'max_length': 'El apellido no puede tener más de 100 caracteres.',
        }
    )
    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Correo electrónico",
        error_messages={
            'invalid': 'Ingresa una dirección de correo electrónico válida.',
        }
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        error_messages={
            'required': 'El teléfono es obligatorio.',
            'max_length': 'El teléfono no puede tener más de 20 caracteres.',
        }
    )
    codigo_verificacion = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                r'^\d{4}$', 
                'El código debe tener exactamente 4 dígitos.'
            )
        ],
        help_text="Código de 4 dígitos que se usará para validar modificaciones o cancelaciones. ¡ES IMPORTANTE QUE LO RECUERDES!",
        verbose_name="Código de verificación",
        error_messages={
            'required': 'El código de verificación es obligatorio.',
            'invalid': 'El código debe tener exactamente 4 dígitos.',
            'max_length': 'El código no puede tener más de 4 caracteres.',
        }
    )

    def save(self, *args, **kwargs):
        if not self.numero_cliente:
            self.numero_cliente = get_random_string(4, allowed_chars='0123456789')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.numero_cliente}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Clase(models.Model):
    TIPO_CLASES = [
        ('Reformer', 'Pilates Reformer'),
        ('Cadillac', 'Pilates Cadillac'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CLASES, verbose_name="Tipo de clase")
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA, verbose_name="Día de la semana")
    horario = models.TimeField(verbose_name="Horario")
    cupo_maximo = models.PositiveIntegerField(default=10, verbose_name="Cupo máximo")

    def cupos_disponibles(self):
        """Devuelve la cantidad de cupos disponibles en esta clase"""
        reservas_actuales = self.reserva_set.filter(activa=True).count()
        return self.cupo_maximo - reservas_actuales

    def esta_completa(self):
        """Verifica si la clase está completa"""
        return self.cupos_disponibles() <= 0

    def get_porcentaje_ocupacion(self):
        """Devuelve el porcentaje de ocupación de la clase"""
        reservas_actuales = self.reserva_set.filter(activa=True).count()
        return round((reservas_actuales / self.cupo_maximo) * 100)

    def __str__(self):
        return f"{self.tipo} - {self.dia} {self.horario.strftime('%H:%M')} ({self.cupos_disponibles()}/{self.cupo_maximo} disponibles)"

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases"
        unique_together = ['tipo', 'dia', 'horario']  # Evita clases duplicadas
        ordering = ['dia', 'horario']

class Reserva(models.Model):
    """
    Reserva recurrente de un cliente a una clase específica.
    El cliente asiste todas las semanas al mismo día y horario.
    """
    numero_reserva = models.CharField(max_length=10, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, verbose_name="Clase")
    fecha_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de reserva")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")
    activa = models.BooleanField(default=True, verbose_name="Reserva activa")

    def save(self, *args, **kwargs):
        if not self.numero_reserva:
            self.numero_reserva = get_random_string(10)
        super().save(*args, **kwargs)

    def puede_modificarse(self):
        """
        Verifica si la reserva puede modificarse (12 horas de anticipación).
        Calcula basándose en el próximo día de clase.
        """
        if not self.activa:
            return False, "La reserva está cancelada"
        
        # Obtener el día de la semana actual
        hoy = timezone.now()
        dias_semana = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4
        }
        
        dia_clase = dias_semana.get(self.clase.dia)
        if dia_clase is None:
            return False, "Día de clase inválido"
        
        # Encontrar la próxima fecha de esta clase
        dias_hasta_clase = (dia_clase - hoy.weekday()) % 7
        if dias_hasta_clase == 0:  # Es hoy
            proxima_clase = hoy.replace(hour=self.clase.horario.hour, minute=self.clase.horario.minute, second=0, microsecond=0)
            if proxima_clase <= hoy:  # La clase ya pasó hoy
                dias_hasta_clase = 7
        
        if dias_hasta_clase == 0:
            proxima_fecha_clase = hoy.replace(hour=self.clase.horario.hour, minute=self.clase.horario.minute, second=0, microsecond=0)
        else:
            proxima_fecha_clase = hoy + timedelta(days=dias_hasta_clase)
            proxima_fecha_clase = proxima_fecha_clase.replace(hour=self.clase.horario.hour, minute=self.clase.horario.minute, second=0, microsecond=0)
        
        # Verificar si faltan más de 12 horas
        tiempo_limite = proxima_fecha_clase - timedelta(hours=12)
        
        if hoy >= tiempo_limite:
            horas_restantes = (proxima_fecha_clase - hoy).total_seconds() / 3600
            return False, f"Solo puedes modificar tu reserva con 12 horas de anticipación. Próxima clase en {horas_restantes:.1f} horas."
        
        return True, "Puedes modificar tu reserva"

    def get_proxima_clase_info(self):
        """Devuelve información sobre cuándo es la próxima clase"""
        hoy = timezone.now()
        dias_semana = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4
        }
        
        dia_clase = dias_semana.get(self.clase.dia)
        if dia_clase is None:
            return "Día inválido"
        
        # Encontrar la próxima fecha de esta clase
        dias_hasta_clase = (dia_clase - hoy.weekday()) % 7
        if dias_hasta_clase == 0:  # Es hoy
            proxima_clase = hoy.replace(hour=self.clase.horario.hour, minute=self.clase.horario.minute, second=0, microsecond=0)
            if proxima_clase <= hoy:  # La clase ya pasó hoy
                dias_hasta_clase = 7
        
        if dias_hasta_clase == 0:
            return "Hoy a las " + self.clase.horario.strftime('%H:%M')
        elif dias_hasta_clase == 1:
            return "Mañana a las " + self.clase.horario.strftime('%H:%M')
        else:
            return f"En {dias_hasta_clase} días ({self.clase.dia} a las {self.clase.horario.strftime('%H:%M')})"

    def __str__(self):
        estado = "Activa" if self.activa else "Cancelada"
        return f"Reserva {self.numero_reserva} - {self.cliente} - {self.clase} ({estado})"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        unique_together = ['cliente', 'clase']  # Un cliente no puede tener múltiples reservas para la misma clase
        ordering = ['-fecha_reserva']

# Modelo Turno por compatibilidad, pero ahora será para casos especiales
# o fechas específicas si en el futuro se necesita.
class Turno(models.Model):
    numero_turno = models.CharField(max_length=10, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, verbose_name="Clase")
    fecha = models.DateField(verbose_name="Fecha del turno")

    def save(self, *args, **kwargs):
        if not self.numero_turno:
            self.numero_turno = get_random_string(10)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.cliente} - {self.fecha}"

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"