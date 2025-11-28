from django.db import models
from django.conf import settings
from classroom.models import Classroom
import uuid
import os

def get_assignment_file_path(instance, filename):
    """Generate a unique file path for assignment files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('assignments/', filename)

def get_submission_file_path(instance, filename):
    """Generate a unique file path for submission files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('assignments/submissions/', filename)

class Assignment(models.Model):
    """
    Model representing an assignment in a classroom.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    points_possible = models.IntegerField(default=100)
    instructions = models.TextField(blank=True, null=True)
    attachment = models.FileField(
        upload_to=get_assignment_file_path,
        blank=True, 
        null=True
    )
    is_published = models.BooleanField(default=True)
    is_draft = models.BooleanField(default=False)
    allow_late_submissions = models.BooleanField(default=True)
    late_penalty_percentage = models.PositiveIntegerField(default=0)  # Percentage penalty for late submissions
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        
    @property
    def submission_count(self):
        return self.submissions.count()
    
    @property
    def graded_count(self):
        return self.submissions.filter(is_graded=True).count()


class AssignmentSubmission(models.Model):
    """
    Model representing a submission for an assignment.
    """
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(
        upload_to=get_submission_file_path,
        blank=True, 
        null=True
    )
    is_late = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    points_earned = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='graded_submissions',
        null=True, 
        blank=True
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    @property
    def is_on_time(self):
        return not self.is_late
    
    @property
    def has_attachment(self):
        return bool(self.attachment)


class Comment(models.Model):
    """
    Model for comments on assignments or submissions
    """
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Polymorphic relationship - can be linked to either an assignment or a submission
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE,
        related_name='comments',
        null=True, 
        blank=True
    )
    submission = models.ForeignKey(
        AssignmentSubmission, 
        on_delete=models.CASCADE,
        related_name='comments',
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"Comment by {self.author.username}"
    
    class Meta:
        ordering = ['created_at']
