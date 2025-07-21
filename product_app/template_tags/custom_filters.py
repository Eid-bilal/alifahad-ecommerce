from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get the value from dictionary by key."""
    try:
        return dictionary.get(int(key), None)  # Convert key to integer before accessing
    except (ValueError, TypeError):
        return None
