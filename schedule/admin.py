from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import Stream, Bundle, TimeSlot, Assessment, Attendance
from users.models import User


TimeSlotForm = select2_modelform(TimeSlot, attrs={'width': '400px'})

class TimeSlotInLine(admin.TabularInline):
    model = TimeSlot
    form = TimeSlotForm
    ordering = ("-id",)

    fields = ['id', 'date', 'time', 'competence', 'week_number']
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


StreamForm = select2_modelform(Stream, attrs={'width': '400px'})

@admin.register(Stream)
class Stream(admin.ModelAdmin):
    form = StreamForm
    inlines = [TimeSlotInLine,]
    list_display = (
        'id',
        'bundle',
        'start_date',
        'get_participants'
    )

    def get_participants(self, stream):
        return len(User.objects.filter(streams=stream.id))
    get_participants.short_description='Кол-во участников'


BundleForm = select2_modelform(Bundle, attrs={'width': '400px'})

@admin.register(Bundle)
class Bundle(admin.ModelAdmin):
    form = BundleForm
    list_display = (
        'id',
        'name',
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'timeslot',
        'is_attend'
    )

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    form = TimeSlotForm
    list_display = ( 
        '__str__',
        'stream',
        'education_center',
        'online', 
        'workshop'
    )
