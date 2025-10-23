from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import User, UserProfile
from .forms import (CustomUserCreationForm, CustomUserChangeForm, 
                   UserProfileForm, UserPreferencesForm, SocialLinksForm)

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('analytics:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Account created for {self.object.username}!')
        return response

class ProfileView(DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.request.user == self.object
        return context

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated!')
        return super().form_valid(form)

@login_required
def profile_settings(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        preferences_form = UserPreferencesForm(request.POST, instance=user)
        social_form = SocialLinksForm(request.POST, instance=user)
        
        if profile_form.is_valid() and preferences_form.is_valid() and social_form.is_valid():
            profile_form.save()
            preferences_form.save()
            social_form.save()
            messages.success(request, 'Your settings have been updated!')
            return redirect('accounts:settings')
    else:
        profile_form = UserProfileForm(instance=profile)
        preferences_form = UserPreferencesForm(instance=user)
        social_form = SocialLinksForm(instance=user)
    
    context = {
        'profile_form': profile_form,
        'preferences_form': preferences_form,
        'social_form': social_form,
    }
    
    return render(request, 'accounts/settings.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def user_dashboard(request):
    user = request.user
    profile = user.profile
    
    # This would typically get data from other apps
    context = {
        'user': user,
        'profile': profile,
        'recent_activity': [],  # Would come from analytics
        'current_courses': [],  # Would come from courses app
        'recent_notes': [],     # Would come from notes app
    }
    
    return render(request, 'accounts/dashboard.html', context)

def custom_logout(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')