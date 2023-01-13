from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, RelatedDropdownFilter

from .models import Region, City, CityType, TerAdministration, Address

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ['city__name', 'street']
    list_display = (
        'city',
        'street',
        'building_number',
        'floor',
        'apartment'
    )
    list_filter = ( 
        ('city', RelatedOnlyDropdownFilter),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(CityType)
class CityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(TerAdministration)
class TerAdministrationAdmin(admin.ModelAdmin):
    pass
