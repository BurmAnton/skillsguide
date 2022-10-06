from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter

from .models import School, Grade, SchoolContactPersone, SchoolStudent


class GradeInLine(admin.TabularInline):
    model = Grade
    #form = GradeForm
    ordering = ("grade",)
    fields = ['grade', 'grade_letter', 'is_graduated']

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'ter_administration', 'address')
    search_fields = ('name', 'inn', 'address__city__name')
    list_filter = (
        ('ter_administration', RelatedOnlyDropdownFilter), 
    )
    inlines = [GradeInLine,]
    
@admin.register(Grade)
class SchoolClassAdmin(admin.ModelAdmin):
    pass

@admin.register(SchoolContactPersone)
class SchoolContactPersoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    search_fields = ('user__last_name', 'school__name', 'school__inn')

@admin.register(SchoolStudent)
class SchoolStudentAdmin(admin.ModelAdmin):
    pass