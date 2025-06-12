from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Reserva, Clase
from .forms import ReservaForm, ModificarReservaForm, EliminarReservaForm, BuscarReservaForm
import json
from accounts.models import UserProfile


# Página de inicio (pública)
def home(request):
    """Vista pública de la página principal"""
    return render(request, 'PilatesGravity/home.html')


# Vista para reservar una clase (solo usuarios autenticados)
@login_required
def reservar_clase(request):
    """
    Permite a un usuario autenticado crear una nueva reserva.
    Utiliza ReservaForm que ya tiene todas las validaciones necesarias.
    """
    if request.method == 'POST':
        form = ReservaForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # El formulario ya validó todo y nos devuelve la clase en cleaned_data
                clase = form.cleaned_data['clase']
                
                # Crear la reserva
                reserva = Reserva.objects.create(
                    usuario=request.user,
                    clase=clase
                )
                
                messages.success(
                    request,
                    f'¡Reserva exitosa! Tu número de reserva es {reserva.numero_reserva}. '
                    f'Asistirás todos los {clase.dia} a las {clase.horario.strftime("%H:%M")} '
                    f'a la clase de {clase.get_tipo_display()}.'
                )
                
                return redirect('PilatesGravity:home')
                
            except IntegrityError:
                # Error de duplicado - no debería ocurrir por las validaciones del form
                messages.error(
                    request,
                    'Error interno: Ya tienes una reserva para esta clase. '
                    'Si esto persiste, contacta al administrador.'
                )
    else:
        # Permitir preseleccionar tipo de clase desde URL
        tipo_preseleccionado = request.GET.get('tipo', '')
        initial_data = {'tipo_clase': tipo_preseleccionado} if tipo_preseleccionado else None
        form = ReservaForm(user=request.user, initial=initial_data)

    return render(request, 'PilatesGravity/reservar_clase.html', {
        'form': form
    })


# Vista para modificar una reserva existente
@login_required
def modificar_reserva(request, numero_reserva):
    """
    Permite a un usuario modificar su propia reserva.
    Utiliza ModificarReservaForm con todas las validaciones.
    """
    # Obtener la reserva y verificar que pertenece al usuario
    reserva = get_object_or_404(
        Reserva, 
        numero_reserva=numero_reserva, 
        usuario=request.user, 
        activa=True
    )
    
    # Verificar si la reserva puede modificarse (12 horas de anticipación)
    puede_modificar, mensaje = reserva.puede_modificarse()
    
    if not puede_modificar:
        messages.error(request, f'No puedes modificar esta reserva: {mensaje}')
        return redirect('PilatesGravity:detalle_reserva', numero_reserva=numero_reserva)

    if request.method == 'POST':
        form = ModificarReservaForm(
            request.POST, 
            reserva_actual=reserva, 
            user=request.user
        )
        
        if form.is_valid():
            try:
                nueva_clase = form.cleaned_data['nueva_clase']
                
                # Actualizar la reserva
                reserva.clase = nueva_clase
                reserva.save()
                
                messages.success(
                    request,
                    f'¡Cambio exitoso! Tu reserva ahora es para la clase de '
                    f'{nueva_clase.get_tipo_display()} los {nueva_clase.dia} '
                    f'a las {nueva_clase.horario.strftime("%H:%M")}.'
                )
                
                return redirect('PilatesGravity:detalle_reserva', numero_reserva=numero_reserva)
                
            except IntegrityError:
                messages.error(
                    request,
                    'Error interno: conflicto de reserva. '
                    'Si esto persiste, contacta al administrador.'
                )
    else:
        form = ModificarReservaForm(reserva_actual=reserva, user=request.user)

    return render(request, 'PilatesGravity/modificar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'puede_modificar': puede_modificar,
        'mensaje_restriccion': mensaje if not puede_modificar else None
    })


# Vista para eliminar/cancelar una reserva
@login_required
def eliminar_reserva(request, numero_reserva):
    """
    Permite a un usuario cancelar su propia reserva.
    Utiliza EliminarReservaForm con validación de confirmación.
    """
    # Obtener la reserva y verificar que pertenece al usuario
    reserva = get_object_or_404(
        Reserva, 
        numero_reserva=numero_reserva, 
        usuario=request.user, 
        activa=True
    )
    
    # Verificar si la reserva puede modificarse (12 horas de anticipación)
    puede_cancelar, mensaje = reserva.puede_modificarse()
    
    if not puede_cancelar:
        messages.error(request, f'No puedes cancelar esta reserva: {mensaje}')
        return redirect('PilatesGravity:detalle_reserva', numero_reserva=numero_reserva)

    if request.method == 'POST':
        form = EliminarReservaForm(
            request.POST, 
            reserva=reserva, 
            user=request.user
        )
        
        if form.is_valid():
            # Cancelar la reserva
            reserva.activa = False
            reserva.save()
            
            messages.success(
                request,
                f'Tu reserva para la clase de {reserva.clase.get_tipo_display()} '
                f'los {reserva.clase.dia} a las {reserva.clase.horario.strftime("%H:%M")} '
                'ha sido cancelada exitosamente.'
            )
            
            return redirect('PilatesGravity:home')
    else:
        form = EliminarReservaForm(reserva=reserva, user=request.user)

    return render(request, 'PilatesGravity/eliminar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'puede_cancelar': puede_cancelar,
        'mensaje_restriccion': mensaje if not puede_cancelar else None
    })


# Vista para buscar reservas de usuario (pública)
def buscar_reservas_usuario(request):
    """
    Permite buscar reservas por nombre de usuario.
    Utiliza BuscarReservaForm para validar el usuario.
    """
    reservas_usuario = []
    usuario_encontrado = None
    
    if request.method == 'POST':
        form = BuscarReservaForm(request.POST)
        
        if form.is_valid():
            # El formulario ya validó que el usuario existe
            usuario_encontrado = form.cleaned_data.get('user')
            
            if usuario_encontrado:
                # Obtener todas las reservas activas del usuario
                reservas_usuario = Reserva.objects.filter(
                    usuario=usuario_encontrado,
                    activa=True
                ).select_related('clase').order_by('clase__dia', 'clase__horario')
    else:
        form = BuscarReservaForm()

    return render(request, 'PilatesGravity/buscar_reservas_usuario.html', {
        'form': form,
        'reservas_usuario': reservas_usuario,
        'usuario_encontrado': usuario_encontrado
    })

# Vista para mostrar detalle de una reserva
def detalle_reserva(request, numero_reserva):
    """
    Muestra el detalle de una reserva específica.
    Solo el dueño de la reserva puede verla (o admin más adelante).
    """
    reserva = get_object_or_404(Reserva, numero_reserva=numero_reserva, activa=True)
    
    # Verificar permisos: solo el dueño puede ver su reserva
    if request.user.is_authenticated and request.user == reserva.usuario:
        puede_ver = True
        es_propietario = True
    else:
        # Para usuarios no autenticados o que no son dueños, no mostrar
        puede_ver = False
        es_propietario = False
    
    if not puede_ver:
        messages.error(request, 'No tienes permisos para ver esta reserva.')
        return redirect('PilatesGravity:home')
    
    # Obtener información sobre si puede modificarse
    puede_modificar, mensaje_modificacion = reserva.puede_modificarse()
    
    return render(request, 'PilatesGravity/detalle_reserva.html', {
        'reserva': reserva,
        'puede_modificar': puede_modificar,
        'mensaje_modificacion': mensaje_modificacion,
        'proxima_clase_info': reserva.get_proxima_clase_info(),
        'es_propietario': es_propietario
    })


# Vista para mostrar clases disponibles (pública)
def clases_disponibles(request):
    """
    Muestra todas las clases disponibles con información de cupos.
    Vista informativa pública.
    """
    clases = Clase.objects.filter(activa=True).order_by('tipo', 'dia', 'horario')
    
    clases_info = []
    for clase in clases:
        clases_info.append({
            'clase': clase,
            'cupos_disponibles': clase.cupos_disponibles(),
            'esta_completa': clase.esta_completa(),
            'porcentaje_ocupacion': clase.get_porcentaje_ocupacion()
        })
    
    return render(request, 'PilatesGravity/clases_disponibles.html', {
        'clases_info': clases_info
    })


# Vista para el botón de "Conoce más" (pública)
def conoce_mas(request):
    """Vista informativa sobre el estudio"""
    return render(request, 'PilatesGravity/conoce_mas.html')


# API Endpoints para funcionalidad AJAX
@require_http_methods(["POST"])
def dias_disponibles(request):
    """
    API que devuelve los días únicos disponibles para un tipo de clase específico
    """
    try:
        data = json.loads(request.body)
        tipo_clase = data.get('tipo')
        
        if not tipo_clase:
            return JsonResponse({'error': 'Tipo de clase requerido'}, status=400)

        # Obtener días únicos para el tipo de clase (solo clases activas)
        dias_disponibles = Clase.objects.filter(
            tipo=tipo_clase, 
            activa=True
        ).values_list('dia', flat=True).distinct()

        # Ordenar días según el orden de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dias_ordenados = sorted(
            set(dias_disponibles), 
            key=lambda x: orden_dias.index(x) if x in orden_dias else 999
        )

        return JsonResponse({
            'dias': dias_ordenados
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def horarios_disponibles(request):
    """
    API que devuelve los horarios disponibles para un tipo de clase y día específicos
    """
    try:
        data = json.loads(request.body)
        tipo_clase = data.get('tipo')
        dia_clase = data.get('dia')
        
        if not tipo_clase or not dia_clase:
            return JsonResponse({'error': 'Tipo de clase y día requeridos'}, status=400)
        
        # Obtener horarios para la combinación tipo-día (solo clases activas)
        clases = Clase.objects.filter(
            tipo=tipo_clase, 
            dia=dia_clase,
            activa=True
        ).order_by('horario')
        
        horarios_info = []
        for clase in clases:
            cupos_disponibles = clase.cupos_disponibles()
            horarios_info.append({
                'value': clase.horario.strftime('%H:%M'),
                'text': f"{clase.horario.strftime('%H:%M')} ({cupos_disponibles} cupos disponibles)",
                'cupos': cupos_disponibles,
                'disponible': cupos_disponibles > 0
            })
        
        return JsonResponse({
            'horarios': horarios_info
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def verificar_disponibilidad(request):
    """
    API que verifica la disponibilidad de una combinación específica tipo-día-horario
    """
    try:
        data = json.loads(request.body)
        tipo_clase = data.get('tipo')
        dia_clase = data.get('dia')
        horario_str = data.get('horario')
        
        if not all([tipo_clase, dia_clase, horario_str]):
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
        
        from datetime import datetime
        horario_time = datetime.strptime(horario_str, '%H:%M').time()
        
        try:
            clase = Clase.objects.get(
                tipo=tipo_clase, 
                dia=dia_clase, 
                horario=horario_time,
                activa=True
            )
            cupos_disponibles = clase.cupos_disponibles()
            
            return JsonResponse({
                'disponible': cupos_disponibles > 0,
                'cupos_disponibles': cupos_disponibles,
                'cupo_maximo': clase.cupo_maximo,
                'mensaje': f'Quedan {cupos_disponibles} cupos disponibles' if cupos_disponibles > 0 else 'Clase completa'
            })
            
        except Clase.DoesNotExist:
            return JsonResponse({
                'disponible': False,
                'mensaje': 'Esta combinación de clase no existe o no está activa'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Formato de horario inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def clases_disponibles_api(request):
    """
    API que devuelve todas las clases disponibles con información de cupos
    """
    try:
        clases = Clase.objects.filter(activa=True).order_by('tipo', 'dia', 'horario')
        
        clases_data = []
        for clase in clases:
            cupos_disponibles = clase.cupos_disponibles()
            clases_data.append({
                'id': clase.id,
                'tipo': clase.tipo,
                'tipo_display': clase.get_tipo_display(),
                'dia': clase.dia,
                'horario': clase.horario.strftime('%H:%M'),
                'horario_display': clase.horario.strftime('%H:%M'),
                'cupos_disponibles': cupos_disponibles,
                'cupo_maximo': clase.cupo_maximo,
                'disponible': cupos_disponibles > 0,
                'porcentaje_ocupacion': clase.get_porcentaje_ocupacion()
            })
        
        return JsonResponse(clases_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)