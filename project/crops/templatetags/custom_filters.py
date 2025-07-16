# crops/templatetags/custom_filters.py
from django import template
import re

register = template.Library()

@register.filter
def replace_chars(value, args=None):
    """
    Replace specified characters in a string with hyphens.
    Usage: {{ value|replace_chars:' ,-' }} (replaces spaces and commas with hyphens)
    """
    if not value or not isinstance(value, str):
        return value
    if args:
        char_map = {arg: '-' for arg in args.split(',')}
        for old, new in char_map.items():
            value = value.replace(old, new)
    return value

# crops/templatetags/custom_filters.py


register = template.Library()

@register.filter
def map_weather_icon(description):
    """
    Map weather descriptions to Font Awesome icon classes.
    Usage: {{ description|map_weather_icon }}
    """
    weather_icon_map = {
        'clear sky': 'sun',
        'few clouds': 'cloud-sun',
        'scattered clouds': 'cloud',
        'broken clouds': 'cloud',
        'shower rain': 'cloud-showers-heavy',
        'rain': 'cloud-rain',
        'thunderstorm': 'bolt',
        'snow': 'snowflake',
        'mist': 'smog',
        # Add more mappings as needed
    }
    return weather_icon_map.get(description.lower(), 'cloud')  # Default to 'cloud' if no match