from django.db import models
from django.conf import settings
from django.utils.text import slugify
from core.image_utils import compress_image
import uuid

def generate_course_code():
    """Generate a unique course code as a string."""
    return str(uuid.uuid4())

class Classroom(models.Model):
    """
    Model representing a virtual classroom.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    course_code = models.CharField(max_length=36, unique=True, default=generate_course_code)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    banner_image = models.ImageField(upload_to='classroom_banners/', blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_classrooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.section}")
        # Compress banner image if provided
        if self.banner_image:
            self.banner_image = compress_image(self.banner_image, max_width=1500, max_height=500, quality=85)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.section}"
    
    @property
    def teacher_count(self):
        return self.members.filter(role='TEACHER').count()
    
    @property
    def student_count(self):
        return self.members.filter(role='STUDENT').count()
    
    @property
    def admin_count(self):
        return self.members.filter(role='ADMIN').count()
    
    class Meta:
        ordering = ['-created_at']


class ClassroomMember(models.Model):
    """
    Model representing a member of a classroom.
    Links users to classrooms with a specific role.
    """
    class Role(models.TextChoices):
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Admin'
    
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE, 
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='enrolled_classrooms'
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} in {self.classroom.name} as {self.role}"
    
    class Meta:
        unique_together = ['classroom', 'user']
        ordering = ['role', 'joined_at']


class Announcement(models.Model):
    """
    Model representing announcements in a classroom.
    """
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE, 
        related_name='announcements'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """
    Model representing comments on announcements.
    """
    announcement = models.ForeignKey(
        Announcement, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.announcement.title}"
    
    class Meta:
        ordering = ['created_at']
