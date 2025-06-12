from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileUpdateForm, UserProfileForm, CambiarPasswordForm
from .models import UserProfile

class CustomLoginView(LoginView):
    """Vista personalizada para el login"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('PilatesGravity:home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos')
        return super().form_invalid(form)

def custom_logout_view(request):
    """Vista personalizada para el logout"""
    if request.method == 'POST':
        # Realizar logout
        logout(request)
        messages.success(request, '¡Has cerrado sesión exitosamente!')
        return redirect('PilatesGravity:home')
    else:
        # Mostrar página de confirmación
        return render(request, 'accounts/logout.html')

def signup(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('PilatesGravity:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, 
                f'¡Cuenta creada exitosamente para {username}! '
                'Ya puedes empezar a reservar tus clases de Pilates.'
            )
            
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            return redirect('accounts:profile_complete')  # Redirigir a completar perfil
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    """Vista para ver/editar información básica del perfil"""
    
    # Asegura que el usuario tenga un perfil 
    try:
        user_profile = request.user.profile
        print(f"DEBUG: Perfil encontrado para {request.user.username}")
        if user_profile.avatar:
            print(f"DEBUG: Avatar existe: {user_profile.avatar.name}")
            print(f"DEBUG: URL del avatar: {user_profile.avatar.url}")
        else:
            print(f"DEBUG: No hay avatar para {request.user.username}")
    except UserProfile.DoesNotExist:
        print(f"DEBUG: Creando perfil para {request.user.username}")
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu información básica ha sido actualizada exitosamente')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ProfileUpdateForm(request.user)
    
    context = {
        'form': form,
        'user_profile': user_profile
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_complete(request):
    """Vista para completar el perfil extendido del usuario"""
    # Obtener o crear el perfil del usuario
    profile, created = request.user.profile, False
    if not hasattr(request.user, 'profile'):
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
        created = True
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.perfil_completado = True
            profile.save()
            
            messages.success(
                request, 
                '¡Tu perfil ha sido completado exitosamente! '
                'Ahora puedes empezar a reservar tus clases.'
            )
            return redirect('PilatesGravity:home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'is_new_profile': created or not profile.perfil_completado
    }
    return render(request, 'accounts/profile_complete.html', context)

@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Mantener la sesión activa después del cambio de contraseña
            update_session_auth_hash(request, request.user)
            messages.success(request, '¡Tu contraseña ha sido cambiada exitosamente!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'accounts/cambiar_password.html', {'form': form})

@login_required
def mis_reservas(request):
    """Vista para mostrar las reservas del usuario actual"""
    reservas_activas = request.user.reservas_pilates.filter(activa=True).select_related('clase')
    reservas_inactivas = request.user.reservas_pilates.filter(activa=False).select_related('clase')[:10]  # Últimas 10 canceladas
    
    context = {
        'reservas_activas': reservas_activas,
        'reservas_inactivas': reservas_inactivas,
        'total_reservas': request.user.reservas_pilates.count()
    }
    return render(request, 'accounts/mis_reservas.html', context)

@login_required
def eliminar_cuenta(request): 
    """Vista para que el usuario pueda eliminar su propia cuenta"""
    if request.method == 'POST':
        # Verificar si tiene reservas activas
        reservas_activas = request.user.reservas_pilates.filter(activa=True)
        
        if reservas_activas.exists():
            messages.error(
                request, 
                'No puedes eliminar tu cuenta mientras tengas reservas activas. '
                'Por favor cancela todas tus reservas primero.'
            )
            return redirect('accounts:eliminar_cuenta')
        
        # Confirmar eliminación
        confirmacion = request.POST.get('confirmar_eliminacion')
        if confirmacion == 'ELIMINAR':
            username = request.user.username
            request.user.delete()
            messages.success(
                request, 
                f'La cuenta de {username} ha sido eliminada exitosamente. '
                '¡Esperamos verte de nuevo pronto!'
            )
            return redirect('PilatesGravity:home')
        else:
            messages.error(request, 'Debes escribir "ELIMINAR" para confirmar la eliminación de tu cuenta.')
    
    # Obtener información para mostrar en la confirmación
    reservas_activas = request.user.reservas_pilates.filter(activa=True)
    
    context = {
        'reservas_activas': reservas_activas,
        'puede_eliminar': not reservas_activas.exists()
    }
    return render(request, 'accounts/eliminar_cuenta.html', context)
