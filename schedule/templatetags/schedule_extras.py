from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def in_status(programs, status):
    return programs.filter(status=status)