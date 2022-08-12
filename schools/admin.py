from django.contrib import admin

from .models import School, Grade, SchoolContactPersone

# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass


@admin.register(Grade)
class SchoolClassAdmin(admin.ModelAdmin):
    pass
