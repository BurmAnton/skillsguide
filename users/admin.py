from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, DisabilityType, Parent
from schedule.models import Bundle


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'middle_name', 'role', 'date_joined', 'is_staff')
    list_filter = (
        ('role', ChoiceDropdownFilter), 
        'is_staff',
    )
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number', 'disability_types')}),
        ('Права доступа',
            {'fields': ('role', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Важные даты', 
            {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('disability_types',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','last_name', 'first_name')
    ordering = ('-date_joined', '-role')


@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    pass

