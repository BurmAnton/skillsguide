from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import Group as OldGroup
from .models import User, Group, Permission, Role
# Register your models here.

admin.site.unregister(OldGroup)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'middle_name', 'role', 'is_staff', 'date_joined')
    list_filter = (
        ('role', ChoiceDropdownFilter), 
        'is_staff',
    )
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number')}),
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
    ordering = ('-date_joined', '-role')


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    pass


#@admin.register(Permission)
#class PermissionAdmin(admin.ModelAdmin):
#    pass