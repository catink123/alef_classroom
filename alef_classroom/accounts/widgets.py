from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html

class CustomClearableFileInput(ClearableFileInput):
    """
    Custom clearable file input widget that displays the checkbox inline with the label.
    """
    template_name = 'django/forms/widgets/clearable_file_input.html'
