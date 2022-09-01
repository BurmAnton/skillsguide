from django.contrib import admin

from .models import School, Grade, SchoolContactPersone, SchoolStudent

# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass


@admin.register(Grade)
class SchoolClassAdmin(admin.ModelAdmin):
    pass

@admin.register(SchoolContactPersone)
class SchoolContactPersoneAdmin(admin.ModelAdmin):
    pass

@admin.register(SchoolStudent)
class SchoolStudentAdmin(admin.ModelAdmin):
    pass