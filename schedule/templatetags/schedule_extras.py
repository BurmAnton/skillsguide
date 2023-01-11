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

@register.filter
def filter_ass(test_ass, student):
    return test_ass.filter(student=student)

@register.filter
def get_attendance(test_attendance, student):
    return test_attendance.get(student=student).is_attend

@register.filter
def check_cycle(cycle):
    for stream in cycle.streams.all():
        if stream.students_limit > stream.students.all().count():
            return True
    return False