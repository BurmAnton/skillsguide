from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from django_admin_listfilter_dropdown.filters import  RelatedOnlyDropdownFilter
from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Group, School, SchoolClass, TerAdministration, City, DisabilityType

@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'get_group', 'is_staff')
    list_filter = (
        ('groups', RelatedOnlyDropdownFilter), 
        'is_staff', 
        'is_active',
    )
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number', 'disability_types')}),
        ('Права доступа',
            {'fields': ('role', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Важные даты', 
            {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','last_name', 'first_name')
    ordering = ('email',)

    def get_group(self, user):
        specialist = Group.objects.filter(name='Специалист по работе с клиентами')
        coordinator_bvb = Group.objects.filter(name='Координатор')
        student = Group.objects.filter(name='Школьник')
        college_rep = Group.objects.filter(name='Представитель ЦО')

        if user.is_superuser:
            return "Админ"

        if len(User.objects.filter(groups__in=specialist, email=user.email)) != 0:
            return "Спец. по работе с клиентами"
        
        if len(User.objects.filter(groups__in=coordinator_bvb, email=user.email)) != 0:
            return "Кординатор БВБ"
                
        if len(User.objects.filter(groups__in=student, email=user.email)) != 0:
            return "Школьник"
                
        if len(User.objects.filter(groups__in=college_rep, email=user.email)) != 0:
            return "Представитель колледжа"

        return "–"
    get_group.short_description = 'Тип пользователя'


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

    list_display = ('name', 'adress', 'specialty')
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
