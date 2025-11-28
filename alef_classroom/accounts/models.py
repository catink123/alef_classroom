from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from core.image_utils import compress_image

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Includes a role field to distinguish between different user types.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        TEACHER = 'TEACHER', _('Teacher')
        STUDENT = 'STUDENT', _('Student')

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Additional fields for contact information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Fields to track user status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Fields for analytics and tracking
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Compress profile picture if provided
        if self.profile_pic:
            self.profile_pic = compress_image(self.profile_pic, max_width=500, max_height=500, quality=85)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class TeacherProfile(models.Model):
    """
    Additional information specific to teachers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    subjects = models.CharField(max_length=255, blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Teacher Profile"


class StudentProfile(models.Model):
    """
    Additional information specific to students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_contact = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Student Profile"
