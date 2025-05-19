from django.contrib import admin
from .models import Cliente, Clase, Turno

admin.site.register(Clase),
admin.site.register(Cliente),
admin.site.register(Turno),
