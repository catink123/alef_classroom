from django import forms
from .models import Classroom, Announcement, Comment


class ClassroomForm(forms.ModelForm):
    """
    Form for creating and editing classrooms.
    """
    class Meta:
        model = Classroom
        fields = ['name', 'description', 'subject', 'section', 'banner_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ClassroomJoinForm(forms.Form):
    """
    Form for joining a classroom using a course code.
    """
    course_code = forms.CharField(
        max_length=36, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter course code'
        })
    )
    
    def clean_course_code(self):
        """
        Clean and normalize the course code.
        Strip whitespace for consistent matching.
        UUIDs are case-insensitive, so we'll do case-insensitive matching in the view.
        """
        course_code = self.cleaned_data.get('course_code', '').strip()
        if not course_code:
            raise forms.ValidationError("Course code cannot be empty.")
        # Just strip whitespace - keep original format for flexible matching
        return course_code


class AnnouncementForm(forms.ModelForm):
    """
    Form for creating and editing announcements.
    """
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Content', 'rows': 5}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CommentForm(forms.ModelForm):
    """
    Form for creating comments on announcements.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment...', 'rows': 2}),
        }
        labels = {
            'content': '',
        }
