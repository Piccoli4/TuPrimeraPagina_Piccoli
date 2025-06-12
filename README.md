# PilatesGravity

Sistema web completo para la gestión de un estudio de pilates, desarrollado con Django 5+ y Python.  
Permite la gestión integral de clases, reservas recurrentes, usuarios y administración del estudio.

---

## 🚀 Características Principales

### Sistema de Reservas
- **Reservas recurrentes**: Una vez creada, se repite semanalmente hasta ser cancelada
- **Validación de disponibilidad**: Control de cupos por clase
- **Restricciones temporales**: Modificación/cancelación con mínimo 12 horas de anticipación
- **Límite diario**: Un usuario no puede tener más de una reserva activa por día

### Gestión de Usuarios
- **Autenticación completa**: Login, registro, perfil, logout
- **Control de acceso**: Solo usuarios autenticados pueden reservar
- **Privacidad**: Los usuarios solo ven y gestionan sus propias reservas

### Administración
- **Panel de administrador**: Creación, edición y eliminación de clases
- **Control de horarios**: Gestión completa de disponibilidad
- **Gestión de cupos**: Control de capacidad por clase

### Interfaz Visual
- **Diseño responsive**: Adaptable a todos los dispositivos
- **Animaciones suaves**: Transiciones fluidas y profesionales
- **Colores personalizados**: Paleta específica (#5D768B, #C8B39B)
- **UX optimizada**: Formularios divididos y validaciones en tiempo real

---

## 📋 Estructura del Proyecto

### Apps Principales
- **PilatesGravity**: Gestión de clases y reservas
- **accounts**: Sistema de autenticación de usuarios

### Modelos de Datos
- **Clase**: Gestión de clases de pilates con horarios y cupos
- **Reserva**: Sistema de reservas recurrentes vinculadas a usuarios
- **Usuario**: Extensión del sistema de usuarios de Django

---

## 🛠 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/TuPrimeraPagina_Piccoli.git
cd TuPrimeraPagina_Piccoli
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario (administrador)
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

### 7. Acceder desde el navegador
```
http://127.0.0.1:8000/
```

---

## 🎯 Guía de Uso

### Para Usuarios (Clientes)
1. **Registro**: Crear cuenta desde "Registrarse"
2. **Login**: Iniciar sesión con credenciales
3. **Reservar**: Seleccionar clase, día y horario deseado
4. **Gestionar**: Ver, modificar o cancelar reservas propias
5. **Perfil**: Actualizar datos personales

### Para Administradores
1. **Panel Admin**: Acceder a `/admin/` con credenciales de superusuario
2. **Crear Clases**: Definir nuevas clases con horarios y cupos
3. **Gestionar Horarios**: Modificar disponibilidad y capacidad
4. **Monitorear Reservas**: Ver todas las reservas del sistema

---

## 🔧 Funcionalidades Técnicas

### Validaciones Implementadas
- Control de cupos disponibles por clase
- Validación de reservas duplicadas por usuario/día
- Verificación de tiempo mínimo para modificaciones (12 horas)
- Autenticación requerida para todas las operaciones de reserva

### Seguridad
- Protección CSRF en todos los formularios
- Control de acceso basado en autenticación
- Validación de permisos por usuario
- Sanitización de datos de entrada

### Características Avanzadas
- Formularios con validación en tiempo real
- Sistema de mensajes de feedback
- Interfaz responsive con CSS3
- Gestión de errores personalizada

---

## 📁 Estructura de Archivos

```
PilatesGravity/
├── PilatesGravity/          # App principal
│   ├── models.py           # Modelos de Clase y Reserva
│   ├── forms.py            # Formularios de reserva
│   ├── views.py            # Vistas de la aplicación
│   ├── urls.py             # URLs de la app
│   └── templates/          # Templates HTML
|   ├── static/                 # Archivos estáticos
|       ├── css/               # Estilos CSS
|       ├── js/                # JavaScript
|       └── images/            # Imágenes
├── accounts/               # App de autenticación
│   ├── models.py           # Extensión de usuarios
│   ├── forms.py            # Formularios de auth
│   ├── views.py            # Vistas de usuarios
│   └── templates/          # Templates de auth
|
└── manage.py              # Comando principal Django
```

---

## 🎨 Personalización Visual

### Colores del Tema
- **Primario**: #5D768B (Azul grisáceo)
- **Secundario**: #C8B39B (Beige dorado)
- **Acentos**: Derivados de los colores principales

### Características de Diseño
- Transiciones CSS suaves (0.3s ease)
- Botones con efectos hover
- Cards con sombras sutiles
- Tipografía legible y moderna

---

## 🔄 Mantenimiento de Datos

### Limpiar datos de prueba
```bash
# Método 1: Reset completo
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Próximas Funcionalidades

- [ ] Sistema de notificaciones por email
- [ ] Calendario visual de reservas
- [ ] Reportes de asistencia
- [ ] Sistema de pagos integrado
- [ ] App móvil complementaria

---

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, crear un issue en el repositorio de GitHub.

---

## 👨‍💻 Desarrollado por

```
Piccoli Guido Augusto
Python - Coderhouse
Proyecto: Sistema PilatesGravity
Tecnologías: Django 5+, Python, HTML5, CSS3, JavaScript
Junio 2025
```

---
