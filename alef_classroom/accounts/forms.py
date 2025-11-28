from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User, TeacherProfile, StudentProfile
from .widgets import CustomClearableFileInput

class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration with additional fields.
    Excludes ADMIN role - admins can only be created through Django admin panel.
    """
    ROLE_CHOICES = [choice for choice in User.Role.choices if choice[0] != 'ADMIN']
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Profile creation is handled by the post_save signal in signals.py
                
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating user profile.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'bio', 'profile_pic', 
                  'phone_number', 'address')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use custom clearable file input widget
        self.fields['profile_pic'].widget = CustomClearableFileInput()


class TeacherProfileForm(forms.ModelForm):
    """
    Form for updating teacher-specific profile information.
    """
    class Meta:
        model = TeacherProfile
        fields = ('department', 'subjects', 'qualification')


class StudentProfileForm(forms.ModelForm):
    """
    Form for updating student-specific profile information.
    """
    class Meta:
        model = StudentProfile
        fields = ('student_id', 'grade_level', 'guardian_name', 'guardian_contact')


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with improved styling.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 
                                                            'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 
                                                                'placeholder': 'Password'}))


