from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, RelatedDropdownFilter

from .models import Assessment, Attendance, Training, TrainingBundle, TrainingCycle, SchoolQuota, TrainingStream, ProfTest, AvailableDate
from users.models import User

@admin.register(TrainingBundle)
class TrainingBundleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    filter_horizontal = ('fields_of_activity', 'competencies')


@admin.register(TrainingCycle)
class TrainingCycleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_date',
        'end_date',
        'region',
        'city',
        'is_active'
    )
    filter_horizontal = ('education_centers', 'programs', 'schools', 'students')


TestForm = select2_modelform(ProfTest, attrs={'width': '400px'})

class ProfTestInline(admin.TabularInline):
    form = TestForm
    model = ProfTest
    fields = ['program', 'date', 'start_time']

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


TrainingStreamForm = select2_modelform(TrainingStream, attrs={'width': '400px'})

@admin.register(TrainingStream)
class TrainingStreamAdmin(admin.ModelAdmin):
    form = TrainingStreamForm
    inlines = [ProfTestInline,]
    search_fields = ['cycle__name', 'id']
    list_display = (
        'id',
        'cycle',
        'student_count'
    )
    list_filter = (
        ('cycle', RelatedOnlyDropdownFilter),
    )

    def student_count(self, stream):
        student_count = len(stream.students.all())
        return f'{student_count}/{stream.students_limit}'
    student_count.short_description='Участники'

    filter_horizontal = ('students',)
    

@admin.register(ProfTest)
class ProfTestAdmin(admin.ModelAdmin):
    search_fields = ['program', 'trainer']
    list_filter = (
        ('program', RelatedOnlyDropdownFilter),
        ('stream', RelatedOnlyDropdownFilter),
        ('ed_center', RelatedOnlyDropdownFilter),
        ('date', DropdownFilter), 
        ('start_time', DropdownFilter)
     )
    list_display = (
        'program',
        'stream',
        'ed_center',
        'date',
        'start_time',
        'student_count',
        'stream',
        'trainer'
    )
    def student_count(self, test):
        student_count = len(test.students.all())
        return f'{student_count}/{test.stream.students_limit}'
    student_count.short_description='Участники'
    filter_horizontal = ('students',)

@admin.register(SchoolQuota)
class SchoolQuotaAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'training_cycle',
        'quota'
    )    


AssessmentForm = select2_modelform(Assessment, attrs={'width': '400px'})

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm

    search_fields = ['test__program__name', 'criterion__name', 'student__user__first_name', 'student__user__last_name', 'student__user__middle_name']
    list_display = (
        'test',
        'student',
        'criterion',
        'grade',
    )


AttendanceForm = select2_modelform(Attendance, attrs={'width': '400px'})

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    form = AttendanceForm
    search_fields = ['test__program__name', 'student__user__first_name', 'student__user__last_name', 'student__user__middle_name']
    list_filter = ( 
        ('test', RelatedOnlyDropdownFilter),
        'is_attend',
        )
    list_display = (
        'student',
        'test',
        'is_attend'
    )

