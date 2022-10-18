from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import Assessment, Attendance, TrainingCycle, SchoolQuota
from users.models import User


@admin.register(TrainingCycle)
class TrainingCycleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_date',
        'end_date',
        'region',
        'city',
        'is_active'
    )


@admin.register(SchoolQuota)
class SchoolQuotaAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'training_cycle',
        'quota'
    )    


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'criterion',
        'grade',
        'timeslot'
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'is_attend'
    )
