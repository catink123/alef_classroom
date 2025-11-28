from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from .forms import (
    CustomUserCreationForm, CustomUserChangeForm,
    TeacherProfileForm, StudentProfileForm,
    CustomAuthenticationForm
)
from .models import User, TeacherProfile, StudentProfile

def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """
    User login view.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next', 'accounts:profile')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@login_required
def user_detail(request, username):
    """
    View user details (public profile).
    """
    user = get_object_or_404(User, username=username)
    
    # Get the appropriate profile based on user role
    if user.role == User.Role.TEACHER:
        try:
            profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            profile = None
        profile_type = 'teacher'
    elif user.role == User.Role.STUDENT:
        try:
            profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            profile = None
        profile_type = 'student'
    else:
        profile = None
        profile_type = 'admin'
    
    context = {
        'viewed_user': user,
        'profile': profile,
        'profile_type': profile_type,
    }
    
    return render(request, 'accounts/user_detail.html', context)

@login_required
def profile(request):
    """
    User profile view with role-specific profile editing.
    """
    user = request.user
    user_form = CustomUserChangeForm(instance=user)
    
    # Get the appropriate profile form based on user role
    if user.role == User.Role.TEACHER:
        profile, created = TeacherProfile.objects.get_or_create(user=user)
        profile_form = TeacherProfileForm(instance=profile)
        profile_type = 'teacher'
    elif user.role == User.Role.STUDENT:
        profile, created = StudentProfile.objects.get_or_create(user=user)
        profile_form = StudentProfileForm(instance=profile)
        profile_type = 'student'
    else:
        profile_form = None
        profile_type = 'admin'
        profile = None
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        
        if profile_form:
            profile_form = (TeacherProfileForm if profile_type == 'teacher' else StudentProfileForm)(
                request.POST, instance=profile
            )
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('accounts:profile')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('accounts:profile')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_type': profile_type,
    }
    
    return render(request, 'accounts/profile.html', context)
