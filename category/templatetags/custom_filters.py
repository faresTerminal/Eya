from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key)


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Returns the value for the given key in a dictionary."""
    return dictionary.get(key)