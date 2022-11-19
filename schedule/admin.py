from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, RelatedDropdownFilter

from .models import Assessment, Attendance, Training, TrainingBundle, TrainingCycle, SchoolQuota, TrainingStream, ProfTest, AvailableDate
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
     list_display = (
        'cycle',
        'id'
     )

@admin.register(ProfTest)
class ProfTestAdmin(admin.ModelAdmin):
    search_fields = ['program', 'trainer']
    list_filter = (
        ('program', RelatedOnlyDropdownFilter),
        ('ed_center', RelatedOnlyDropdownFilter),
        ('date', DropdownFilter), 
        ('start_time', DropdownFilter)
     )
    list_display = (
        'program',
        'ed_center',
        'date',
        'start_time',
        'stream',
        'trainer'
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
        'student',
        'criterion',
        'grade',
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'is_attend'
    )
