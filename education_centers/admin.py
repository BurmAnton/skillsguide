from dataclasses import fields
from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter
from openpyxl import Workbook

from .models import FieldOfActivity, Competence, EducationCenter, TrainingProgram, Criterion, Workshop, Trainer

# Register your models here.
@admin.register(FieldOfActivity)
class FieldOfActivityAdmin(admin.ModelAdmin):
    pass


CompetenceForm = select2_modelform(Competence, attrs={'width': '400px'})

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    form = CompetenceForm
    list_filter = ('field_of_activity', 'is_ws')
    search_fields = ['name']
    list_display = [
        'id',
        'name', 
        'field_of_activity', 
        'is_ws'
    ]

EducationCenterForm = select2_modelform(EducationCenter, attrs={'width': '400px'})

@admin.register(EducationCenter)
class EducationCenterAdmin(admin.ModelAdmin):
    form = EducationCenterForm
    
    search_fields = ['name', 'short_name']
    list_display = [
        'short_name',
        'name',
        'address',
        'is_trains'
    ]


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    pass


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    pass

CriterionForm = select2_modelform(Criterion, attrs={'width': '400px'})

class CriterionInline(admin.TabularInline):
    form = CriterionForm
    model = Criterion


TrainingProgramForm = select2_modelform(TrainingProgram, attrs={'width': '400px'})

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    form = TrainingProgramForm
    inlines = [CriterionInline,]
    search_fields = ['name']
    readonly_fields = ['get_criteria',]
    list_display = [
        'name',
        'competence',
        'program_type',
        'education_center',
        'status',
        'get_criteria'
    ]
    
    def get_criteria(self, program):
        criteria = len(program.criteria.all())
        return criteria
    get_criteria.short_description='Колво критериев'

    actions = ['approve_status', 'check_status', 'deny_status']
    def approve_status(self, request, queryset):
        queryset.update(status='PRF')
    approve_status.short_description='Изменить статус на "Одобрен"'

    def check_status(self, request, queryset):
        queryset.update(status='CHCK')
    check_status.short_description='Изменить статус на "На проверке"'

    def deny_status(self, request, queryset):
        queryset.update(status='DN')
    deny_status.short_description='Изменить статус на "Отказано"'

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    pass