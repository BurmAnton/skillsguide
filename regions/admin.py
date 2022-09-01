from django.contrib import admin

from .models import Region, City, CityType, TerAdministration, Address

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(CityType)
class CityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(TerAdministration)
class TerAdministrationAdmin(admin.ModelAdmin):
    pass
