from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from .models import User, TeacherProfile, StudentProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create the appropriate profile when a new user is created.
    """
    if created:
        try:
            if instance.role == User.Role.TEACHER:
                TeacherProfile.objects.get_or_create(user=instance)
            elif instance.role == User.Role.STUDENT:
                StudentProfile.objects.get_or_create(user=instance)
        except IntegrityError:
            # Profile already exists, ignore the error
            pass
