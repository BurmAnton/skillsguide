from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter
from django.utils.safestring import mark_safe
from django.urls import reverse

from easy_select2 import select2_modelform

from .models import School, Grade, SchoolContactPersone, SchoolStudent

GradeForm = select2_modelform(Grade, attrs={'width': '400px'})

class GradeInLine(admin.TabularInline):
    model = Grade
    form = GradeForm
    ordering = ("grade",)
    fields = ['grade', 'grade_letter', 'is_graduated']

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_inn', 'ter_administration', 'address', 'get_students_count')
    search_fields = ('name', 'inn', 'address__city__name')
    list_filter = (
        ('ter_administration', RelatedOnlyDropdownFilter), 
    )
    inlines = [GradeInLine,]

    def get_inn(self, school):
        school_url = reverse("school_profile", args=[school.id])
        school_inn = school.inn
        school_link = f'<a href="{school_url}" target="_blank">{school_inn}</a>'
        return mark_safe(school_link)
    get_inn.short_description = 'ИНН'
    get_inn.admin_order_field = 'inn'

    def get_students_count(self, school):
        students_count = len(school.students.all())
        return students_count
    get_students_count.short_description='Колво учеников'


StudentsForm = select2_modelform(SchoolStudent, attrs={'width': '400px'})

class StudentsInLine(admin.TabularInline):
    model = SchoolStudent
    form = StudentsForm
    ordering = ("grade",)
    fields = ['user',]

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

GradeForm = select2_modelform(Grade, attrs={'width': '400px'})

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    form = GradeForm
    inlines = [StudentsInLine,]
    search_fields = ('school__name', 'grade', 'grade_letter')
    list_display = ('school', 'grade', 'grade_letter', 'get_students_count', 'is_graduated')
    list_filter = (
        ('school', RelatedOnlyDropdownFilter),
        ('grade', DropdownFilter),
        ('grade_letter', DropdownFilter),
    )

    def get_students_count(self, grade):
        students_count = len(grade.students.all())
        return students_count
    get_students_count.short_description='Колво учеников'

@admin.register(SchoolContactPersone)
class SchoolContactPersoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    search_fields = ('user__last_name', 'school__name', 'school__inn')

@admin.register(SchoolStudent)
class SchoolStudentAdmin(admin.ModelAdmin):
    search_fields = ('user__last_name', 'user__middle_name', 'user__first_name', 'school__name', 'school__inn')
    list_display = ('get_last_name', 'get_first_name', 'get_middle_name', 'get_email', 'school', 'get_grade')
    list_filter = (
        ('school', RelatedOnlyDropdownFilter),
        ('grade', RelatedOnlyDropdownFilter),
    )

    def get_last_name(self, student):
        last_name = student.user.last_name
        return last_name
    get_last_name.short_description='Фамилия'
    get_last_name.admin_order_field = 'student__user__last_name'

    def get_first_name(self, student):
        first_name = student.user.first_name
        return first_name
    get_first_name.short_description='Имя'
    get_first_name.admin_order_field = 'student__user__first_name'

    def get_middle_name(self, student):
        middle_name = student.user.middle_name
        return middle_name
    get_middle_name.short_description='Отчество'
    get_middle_name.admin_order_field = 'student__user__middle_name'

    def get_email(self, student):
        student_url = reverse("student_profile", args=[student.user.id])
        email = student.user.email
        profile_link = f'<a href="{student_url}" target="_blank">{email}</a>'
        return mark_safe(profile_link)
    get_email.short_description='Email'
    get_email.admin_order_field = 'student__user__email'

    def get_grade(self, student):
        classes = f'{student.grade.grade}{student.grade.grade_letter}'
        return classes
    get_grade.short_description='Класс'
    get_grade.admin_order_field = 'student__grade'