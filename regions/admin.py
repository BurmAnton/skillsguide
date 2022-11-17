from django.contrib import admin

from .models import Address, City, Country

# Register your models here.
@admin.register(Country)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(City)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(Address)
class RoleAdmin(admin.ModelAdmin):
    pass