from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def in_status(programs, status):
    return programs.filter(status=status)

@register.filter
def filter_busy(dates):
    return dates.filter(busy=False)

@register.filter
def filter_unavailable(dates):
    return dates.filter(busy=False, is_unavailable=False)

