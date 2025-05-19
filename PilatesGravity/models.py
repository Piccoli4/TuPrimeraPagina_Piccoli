from django.db import models

from django.db import models

# Modelo para clientes
class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.apellido} {self.nombre}"


# Modelo para clases de pilates
class Clase(models.Model):
    nombre = models.CharField(max_length=100)  
    dia = models.CharField(max_length=20)     
    hora = models.TimeField()
    cupo_maximo = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.dia} {self.hora.strftime('%H:%M')}"


# Modelo para turnos
class Turno(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    fecha = models.DateField()
    confirmado = models.BooleanField(default=False)

    def __str__(self):
        return f"Turno de {self.cliente.nombre} para {self.clase.nombre} el {self.fecha}"
