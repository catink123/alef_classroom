from django import template

register = template.Library()

@register.filter
def filename(value):
    """Extract filename from file path."""
    if value:
        return value.split('/')[-1]
    return value

@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
