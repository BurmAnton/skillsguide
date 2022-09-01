from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from django_admin_listfilter_dropdown.filters import  RelatedOnlyDropdownFilter
from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, DisabilityType
from schedule.models import Bundle


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'middle_name', 'get_bundles', 'role', 'is_staff', 'date_joined')
    list_filter = (
        ('groups', RelatedOnlyDropdownFilter), 
        'is_staff', 
        'is_active',
        'bundles'
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

    def get_bundles(self, user):
        bundles = Bundle.objects.filter(participants=user)
        if len(bundles) != 0:
            return list(bundles)
        return "–"
    get_bundles.short_description = 'Выбранные наборы'


@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    pass



