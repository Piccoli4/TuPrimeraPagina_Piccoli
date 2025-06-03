from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Cliente, Reserva, Clase
from .forms import ClienteForm, ReservaForm, BuscarReservaForm, ConfirmarReservaForm, CambiarReservaForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

# Página de inicio
def home(request):
    return render(request, 'PilatesGravity/home.html')

# Vista para reservar una clase (reserva recurrente)
def reservar_clase(request):

    # Obtener el tipo de clase desde la URL (si existe)
    tipo_preseleccionado = request.GET.get('tipo', '')

    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        reserva_form = ReservaForm(request.POST)

        if cliente_form.is_valid() and reserva_form.is_valid():
            try:
                # Primero guardamos el cliente
                cliente = cliente_form.save()
                
                # Obtenemos la clase seleccionada del formulario validado
                clase = reserva_form.cleaned_data['clase']
                
                # Verificamos una vez más que la clase tenga cupo (por seguridad)
                if clase.esta_completa():
                    messages.error(request, 
                        f'Lo sentimos, la clase de {clase.tipo} los {clase.dia} a las {clase.horario.strftime("%H:%M")} '
                        'se completó mientras procesábamos tu reserva. Por favor selecciona otra clase.')
                    
                    # Reiniciamos los formularios para que el usuario pueda intentar de nuevo
                    cliente_form = ClienteForm()
                    reserva_form = ReservaForm(initial={'tipo_clase': tipo_preseleccionado} if tipo_preseleccionado else None)
                else:
                    # Creamos la reserva
                    reserva = Reserva.objects.create(cliente=cliente, clase=clase)
                    
                    messages.success(request, 
                        f'¡Reserva exitosa! Tu número de reserva es {reserva.numero_reserva}. '
                        f'Asistirás todos los {clase.dia} a las {clase.horario.strftime("%H:%M")} '
                        f'a la clase de {clase.tipo}. '
                        f'Recuerda tu código de verificación: es necesario para modificar o cancelar tu reserva.')
                    
                    return redirect('home')
                    
            except IntegrityError:
                # El cliente ya tiene una reserva para esta clase
                messages.error(request, 
                    'Ya tienes una reserva activa para esta clase. '
                    'Si deseas cambiar de clase, primero cancela tu reserva actual.')

    else:
        cliente_form = ClienteForm()
        # Si hay un tipo preseleccionado, inicializar el formulario con ese valor
        initial_data = {'tipo_clase': tipo_preseleccionado} if tipo_preseleccionado else None
        reserva_form = ReservaForm(initial=initial_data)

    return render(request, 'PilatesGravity/reservar_clase.html', {
        'cliente_form': cliente_form,
        'reserva_form': reserva_form,
        'tipo_preseleccionado': tipo_preseleccionado  # Pasar al template para JavaScript
    })

# Vista para mostrar clases disponibles (informativa)
def clases_disponibles(request):
    clases = Clase.objects.all().order_by('dia', 'horario')
    
    clases_info = []
    for clase in clases:
        clases_info.append({
            'clase': clase,
            'cupos_disponibles': clase.cupos_disponibles(),
            'esta_completa': clase.esta_completa(),
            'porcentaje_ocupacion': round((clase.cupo_maximo - clase.cupos_disponibles()) / clase.cupo_maximo * 100)
        })
    
    return render(request, 'PilatesGravity/clases_disponibles.html', {
        'clases_info': clases_info
    })

# Vista para buscar reservas por cliente
def buscar_reserva(request):
    resultados = []
    if request.method == 'POST':
        form = BuscarReservaForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            resultados = Reserva.objects.filter(
                cliente__nombre__icontains=nombre,
                cliente__apellido__icontains=apellido,
                activa=True
            ).select_related('cliente', 'clase')
    else:
        form = BuscarReservaForm()
    
    return render(request, 'PilatesGravity/buscar_reserva.html', {
        'form': form,
        'resultados': resultados
    })

# Vista para cancelar una reserva
def cancelar_reserva(request, numero_reserva):
    reserva = get_object_or_404(Reserva, numero_reserva=numero_reserva, activa=True)
    
    # Verificar si la reserva puede modificarse (usando la misma lógica que para cambios)
    puede_modificar, mensaje = reserva.puede_modificarse()
    
    if not puede_modificar:
        messages.error(request, f'No puedes cancelar esta reserva: {mensaje}')
        return redirect('detalle_reserva', numero_reserva=numero_reserva)

    if request.method == 'POST':
        form = ConfirmarReservaForm(request.POST)
        if form.is_valid():
            codigo_ingresado = form.cleaned_data['codigo_verificacion']
            if codigo_ingresado == reserva.cliente.codigo_verificacion:
                reserva.activa = False
                reserva.save()
                
                messages.success(request, 
                    f'Tu reserva para la clase de {reserva.clase.tipo} los {reserva.clase.dia} '
                    f'a las {reserva.clase.horario.strftime("%H:%M")} ha sido cancelada exitosamente.')
                
                return redirect('home')
            else:
                form.add_error('codigo_verificacion', 'El código de verificación es incorrecto.')
    else:
        form = ConfirmarReservaForm()

    return render(request, 'PilatesGravity/cancelar_reserva.html', {
        'reserva': reserva,
        'form': form,
        'puede_cancelar': puede_modificar,
        'mensaje_restriccion': mensaje if not puede_modificar else None
    })

# Vista para cambiar una reserva
def cambiar_reserva(request, numero_reserva):
    reserva = get_object_or_404(Reserva, numero_reserva=numero_reserva, activa=True)
    
    # Verificar si la reserva puede modificarse
    puede_modificar, mensaje = reserva.puede_modificarse()
    
    if not puede_modificar:
        messages.error(request, f'No puedes cambiar esta reserva: {mensaje}')
        return redirect('detalle_reserva', numero_reserva=numero_reserva)

    if request.method == 'POST':
        # Verificar código de verificación primero
        codigo_ingresado = request.POST.get('codigo_verificacion', '')
        if codigo_ingresado != reserva.cliente.codigo_verificacion:
            messages.error(request, 'El código de verificación es incorrecto.')
        else:
            form = CambiarReservaForm(request.POST, reserva_actual=reserva)
            if form.is_valid():
                try:
                    # Obtener la nueva clase
                    nueva_clase = form.cleaned_data['nueva_clase']
                    
                    # Verificar una vez más que la nueva clase tenga cupo
                    if nueva_clase.esta_completa():
                        messages.error(request, 
                            f'Lo sentimos, la clase de {nueva_clase.tipo} los {nueva_clase.dia} '
                            f'a las {nueva_clase.horario.strftime("%H:%M")} se completó mientras procesábamos tu cambio. '
                            'Por favor selecciona otra clase.')
                    else:
                        # Actualizar la reserva
                        reserva.clase = nueva_clase
                        reserva.save()
                        
                        messages.success(request, 
                            f'¡Cambio exitoso! Tu reserva ahora es para la clase de {nueva_clase.tipo} '
                            f'los {nueva_clase.dia} a las {nueva_clase.horario.strftime("%H:%M")}.')
                        
                        return redirect('detalle_reserva', numero_reserva=numero_reserva)
                        
                except IntegrityError:
                    messages.error(request, 
                        'Ya tienes una reserva activa para la clase seleccionada. '
                        'Selecciona una clase diferente.')
            else:
                # Si el formulario no es válido, mostrar los errores
                pass
    else:
        form = CambiarReservaForm(reserva_actual=reserva)

    return render(request, 'PilatesGravity/cambiar_reserva.html', {
        'reserva': reserva,
        'form': form,
        'puede_cambiar': puede_modificar,
        'mensaje_restriccion': mensaje if not puede_modificar else None
    })

# Vista para el botón de "Conoce más"
def conoce_mas(request):
    return render(request, 'PilatesGravity/conoce_mas.html')

# Vista para mostrar el detalle de una reserva
def detalle_reserva(request, numero_reserva):
    reserva = get_object_or_404(Reserva, numero_reserva=numero_reserva, activa=True)
    
    # Obtener información sobre si puede modificarse
    puede_modificar, mensaje_modificacion = reserva.puede_modificarse()
    
    return render(request, 'PilatesGravity/detalle_reserva.html', {
        'reserva': reserva,
        'puede_modificar': puede_modificar,
        'mensaje_modificacion': mensaje_modificacion,
        'proxima_clase_info': reserva.get_proxima_clase_info()
    })

@require_http_methods(["POST"])
@require_http_methods(["POST"])
def dias_disponibles(request):
    """
    Devuelve los días únicos disponibles para un tipo de clase específico
    """
    try:
        data = json.loads(request.body)
        tipo_clase = data.get('tipo')
        
        if not tipo_clase:
            return JsonResponse({'error': 'Tipo de clase requerido'}, status=400)

        # Obtiene todas las clases del tipo seleccionado
        clases = Clase.objects.filter(tipo=tipo_clase).values_list('dia', flat=True)

        # Elimina duplicados usando set
        dias_unicos = list(set(clases))

        # Ordena los días según el orden de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dias_ordenados = sorted(dias_unicos, key=lambda x: orden_dias.index(x) if x in orden_dias else 999)

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
    Devuelve los horarios disponibles para un tipo de clase y día específicos
    """
    try:
        data = json.loads(request.body)
        tipo_clase = data.get('tipo')
        dia_clase = data.get('dia')
        
        if not tipo_clase or not dia_clase:
            return JsonResponse({'error': 'Tipo de clase y día requeridos'}, status=400)
        
        # Obtiene horarios para la combinación tipo-día
        clases = Clase.objects.filter(
            tipo=tipo_clase, 
            dia=dia_clase
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
    Verifica la disponibilidad de una combinación específica tipo-día-horario
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
            clase = Clase.objects.get(tipo=tipo_clase, dia=dia_clase, horario=horario_time)
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
                'mensaje': 'Esta combinación de clase no existe'
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
    Devuelve todas las clases disponibles con información de cupos
    """
    try:
        clases = Clase.objects.all().order_by('tipo', 'dia', 'horario')
        
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
