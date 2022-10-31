from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import Assessment, Attendance, TrainingBundle, TrainingCycle, SchoolQuota, TrainingStream
from users.models import User

@admin.register(TrainingBundle)
class TrainingBundleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    filter_horizontal = ('fields_of_activity', 'competencies')

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
    filter_horizontal = ('education_centers', 'programs', 'schools')


@admin.register(TrainingStream)
class TrainingStreamAdmin(admin.ModelAdmin):
    pass


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
