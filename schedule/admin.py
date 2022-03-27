from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import Stream, Bundle, TimeSlot


TimeSlotForm = select2_modelform(TimeSlot, attrs={'width': '400px'})

class TimeSlotInLine(admin.TabularInline):
    model = TimeSlot
    form = TimeSlotForm
    ordering = ("-id",)
    fields = ['id', 'date', 'time', 'competence']
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
        'start_date'
    )



BundleForm = select2_modelform(Bundle, attrs={'width': '400px'})

@admin.register(Bundle)
class CompBundle(admin.ModelAdmin):
    form = BundleForm
    list_display = (
        'id',
        'name',
    )

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass