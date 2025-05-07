# templatetags/interests_filters.py
import json
from django import template

register = template.Library()

@register.filter
def clean_interests(value):
    try:
        items = json.loads(value)
        return " ".join([item.get("value", "") for item in items]) if isinstance(items, list) else value
    except:
        return value
