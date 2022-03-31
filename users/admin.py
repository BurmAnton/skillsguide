from dataclasses import fields
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from django_admin_listfilter_dropdown.filters import  RelatedOnlyDropdownFilter
from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Group, School, SchoolClass, TerAdministration, City, DisabilityType
from schedule.models import Bundle


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'get_bundles', 'role', 'is_staff')
    list_filter = (
        ('groups', RelatedOnlyDropdownFilter), 
        'is_staff', 
        'is_active',
        'bundles'
    )
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number', 'disability_types')}),
        ("Школа",
        {'fields': ('school', 'school_class')}),
        ('Права доступа',
            {'fields': ('role', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Важные даты', 
            {'fields': ('relocate_status', 'last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','last_name', 'first_name')
    ordering = ('email',)

    def get_bundles(self, user):
        bundles = Bundle.objects.filter(participants=user)
        if len(bundles) != 0:
            return list(bundles)
        return "–"
    get_bundles.short_description = 'Выбранные наборы'


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    pass

@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass

@admin.register(TerAdministration)
class TerAdministrationAdmin(admin.ModelAdmin):
    pass

SchoolClassForm = select2_modelform(SchoolClass, attrs={'width': '400px'})

class SchoolClassInline(admin.TabularInline):
    model = SchoolClass
    form = SchoolClassForm


SchoolForm = select2_modelform(School, attrs={'width': '400px'})

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    form = SchoolForm
    search_fields = ['name', 'adress', 'specialty', 'school_coordinators__email']

    list_display = ('name', 'adress', 'city', 'ter_administration')
    inlines = [SchoolClassInline,]
    fieldsets = (
        (None, {
            'fields': (
                "name",
                "specialty"
            ),
        }),
        ("Местоположение",{
            'fields': (
                "ter_administration",
                "city",
                "adress",
                "inn"
            ),
        }),
    )

UserForm = select2_modelform(User, attrs={'width': '400px'})

class CitizenInline(admin.TabularInline):
    model = User
    form = UserForm
    fieldsets = (
        (None, {
            "fields": (
                "first_name",
                "last_name",
                "middle_name",
                "email"
            ),
        }),
    )
    short_description='Студенты'
    
SchoolClassesForm = select2_modelform(SchoolClass, attrs={'width': '400px'})

@admin.register(SchoolClass)
class SchoolClassesAdmin(admin.ModelAdmin):
    form = SchoolClassesForm
    inlines = [
        CitizenInline
    ]
    list_display = ('grade_number', 'grade_letter', 'school')
    search_fields = ['school', 'grade_number', 'grade_letter', 'students']
    list_filter = (
        ('school', RelatedOnlyDropdownFilter),
        ('grade_number', DropdownFilter), 
        ('grade_letter', DropdownFilter),
    )


