from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherProfile, StudentProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role field.
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Role & Status', {'fields': ('role', 'is_verified', 'last_login_ip')}),
        ('Additional Info', {'fields': ('bio', 'profile_pic', 'phone_number', 'address')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_verified', 'date_joined')
    list_filter = ('role', 'is_active', 'is_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """
    Admin for teacher profiles.
    """
    list_display = ('user', 'department', 'subjects')
    search_fields = ('user__username', 'department', 'subjects')
    list_filter = ('department',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Admin for student profiles.
    """
    list_display = ('user', 'student_id', 'grade_level')
    search_fields = ('user__username', 'student_id')
    list_filter = ('grade_level',)
