from itertools import cycle
import math
from datetime import datetime, timedelta, date
from multiprocessing.dummy import current_process

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.db.models import Sum
#Decorators
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

#Models
from .models import Attendance, Assessment, AvailableDate, ProfTest, TrainingBundle, TrainingCycle, FieldOfActivity, TrainingStream
from users.models import DisabilityType, User
from regions.models import City
from schools.models import School, Grade, SchoolContactPersone, SchoolStudent
from education_centers.models import EducationCenter, TrainingProgram, Competence, Workshop, Criterion


# Create your views here.
def index(request):
    return HttpResponseRedirect(reverse("login"))

@login_required
def student_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(SchoolStudent, user=user)
    school = student.school

    streams = TrainingStream.objects.filter(students=student)
    two_weeks = datetime.today() + timedelta(14)
    tests = ProfTest.objects.filter(stream__in=streams, date__gte=datetime.today(), date__lte=two_weeks).order_by('date', 'start_time')

    passed_tests = ProfTest.objects.filter(stream__in=streams, date__lte=(datetime.today() - timedelta(1))).order_by('date', 'start_time')

    return render(request, "schedule/student_profile.html",{
        'page_name': 'Личный кабинет',
        'user': user,
        'student': student,
        'school': school,
        'tests': tests,
        'passed_tests': passed_tests,
        'date_today': datetime.today(),
        'date_two_weeks': two_weeks
    })

@login_required
@csrf_exempt
def bundles_list(request):
    if request.method == 'POST':
        name = request.POST["name"]
        competencies = request.POST.getlist("competencies")
        fields_of_activity = FieldOfActivity.objects.filter(competencies__in=competencies)
        bundle = TrainingBundle(
            name=name,
        )
        bundle.save()
        bundle.fields_of_activity.add(*fields_of_activity)
        bundle.competencies.add(*competencies)
        bundle.save()
    bundles = TrainingBundle.objects.all()
    cycles = TrainingCycle.objects.all()

    return render(request, "schedule/bundles_list.html", {
        'bundles': bundles,
        'cycles': cycles,
        'fields_of_activity': FieldOfActivity.objects.all,
        'competencies': Competence.objects.all,
        'programs': TrainingProgram.objects.filter(status='PRF', program_type='SP'),
        'cities': City.objects.all,
        'schools': School.objects.all
    })

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

@login_required
@csrf_exempt
def create_cycle(request):
    if request.method == 'POST':
        start_date = datetime.strptime(request.POST["start_date"],"%Y-%m-%d")
        end_date = datetime.strptime(request.POST["end_date"],"%Y-%m-%d")
        if 'edit-cycle' in request.POST:
            cycle_id = request.POST["cycle"]
            name = request.POST["name"]
            cycle = get_object_or_404(TrainingCycle, id=cycle_id)
            cycle.name = name
            cycle.save()
            available_dates = AvailableDate.objects.filter(
                stream__in=cycle.streams.all(), 
                date__lt=start_date,
                busy=False
            )
            available_dates.delete()
            available_dates = AvailableDate.objects.filter(
                stream__in=cycle.streams.all(), 
                date__gt=end_date,
                busy=False
            )
            available_dates.delete()
            programs_count = len(cycle.programs.all())
            excluded_dates = cycle.excluded_dates.split(", 0, 0),")
            excluded_dates = [x+')]' for x in excluded_dates]
            for stream in cycle.streams.all():
                slot_date = start_date
                if cycle.is_any_day == False:
                    days_of_week = list(map(int, cycle.days_of_week))
                    date_limit = programs_count + 2
                else:
                    days_of_week = [0, 1, 2, 3, 4]
                    week_count = math.ceil(programs_count/cycle.days_per_week)+1
                    date_limit = (week_count)*5 + len(excluded_dates)
                while slot_date < end_date:
                    for weekday in days_of_week:
                        if slot_date not in excluded_dates and slot_date.weekday() in days_of_week:
                            avaible_date, is_new = AvailableDate.objects.get_or_create(
                                stream=stream, 
                                date=slot_date,
                                week_number=week_count
                            )
                            avaible_date.save()
                        slot_date = slot_date + timedelta(1)
                        if slot_date < end_date or slot_date.weekday() == 5:
                            week_count -= 1
                            break
            cycle.start_date = start_date
            cycle.end_date = end_date
            cycle.save()
        else:
            bundle_id = request.POST["bundle"]
            bundle = TrainingBundle.objects.get(id=bundle_id)
            name = request.POST["name"]
            programs = []
            education_centers = []
            for competence in bundle.competencies.all():
                programs_list = request.POST.getlist(f'{competence}_programs')
                for program_id in programs_list:
                    program = TrainingProgram.objects.get(id=program_id)
                    programs.append(program)
                    education_centers.append(program.education_center)
            try:
                is_any_day = request.POST["is_any_day"]
                is_any_day = True
            except:
                is_any_day = False
            #Получаем массив дней исключений 
            ex_dates = request.POST["dates"]
            if "," in ex_dates:
                excluded_dates = ex_dates.split(",")
                excluded_dates = [datetime.strptime(x,"%d/%m/%y") for x in excluded_dates]
            else:
                excluded_dates = []
            start_time = datetime.strptime(request.POST["start_time"], "%H:%M").time()
            
            group_limit = int(request.POST["group_limit"])
            students_limit = int(request.POST["students_limit"])
            city = request.POST["city"]
            if city == 'Выберите город':
                city = None
            else:
                city = City.objects.get(id=city)
            cycle = TrainingCycle(
                name=name,
                bundle=bundle,
                city=city,
                students_limit=students_limit,
                group_limit=group_limit,
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                excluded_dates=excluded_dates,
                is_any_day=is_any_day
            )
            cycle.save()
            cycle.programs.add(*programs)
            cycle.education_centers.add(*education_centers)
            cycle.schools.add(*request.POST.getlist("schools"))
            cycle.save()
            if is_any_day == False:
                cycle.days_of_week = request.POST.getlist("days_of_week")
            else:
                cycle.days_per_week = int(request.POST["days_per_week"])
            cycle.save()

            steams_count = math.ceil(students_limit / group_limit)
            excluded_dates = cycle.excluded_dates
            programs_count = len(cycle.programs.all())
            for i in range(steams_count):
                stream = TrainingStream(
                    cycle=cycle,
                    students_limit=group_limit,
                )
                stream.save()

                for program in cycle.programs.all():
                    test = ProfTest(
                        ed_center=program.education_center,
                        program=program,
                        stream=stream,
                        start_time=cycle.start_time
                    )
                    test.save()

                available_dates = []
                slot_date = cycle.start_date
                if cycle.is_any_day == False:
                    days_of_week = list(map(int, cycle.days_of_week))
                    date_limit = programs_count + 2
                else:
                    days_of_week = [0, 1, 2, 3, 4]
                    week_count = math.ceil(programs_count/cycle.days_per_week)+1
                    date_limit = (week_count)*5 + len(excluded_dates)
                while slot_date < end_date:
                    for weekday in days_of_week:
                        if slot_date not in excluded_dates and slot_date.weekday() in days_of_week:
                            avaible_date = AvailableDate(
                                stream=stream, 
                                date=slot_date,
                                week_number=week_count
                            )
                            avaible_date.save()
                        slot_date = slot_date + timedelta(1)
                        if slot_date < end_date or slot_date.weekday() == 5:
                            week_count -= 1
                            break

        return HttpResponseRedirect(reverse("bundles_list")) 
    return HttpResponseRedirect(reverse("login")) 

def stream_schedule(request, stream_id):
    stream = get_object_or_404(TrainingStream, id=stream_id)
    return render(request, "schedule/stream_schedule.html", {
        'stream': stream
    })

def add_soft_skills(request):
    programs = TrainingProgram.objects.all()
    criteria = Criterion.objects.filter(skill_type="SFT")
    for program in programs:
        program.soft_criteria.add(*criteria)
        program.save()
    return HttpResponseRedirect(reverse("login"))

def fix_attendance(request):
    tests = ProfTest.objects.all()
    for test in tests:
        for student in test.students.all():
            assessments = Attendance.objects.filter(test=test, student=student)
            if len(assessments) > 1:
                for assessment in assessments:
                    if assessment.is_attend == False:
                        assessment.delete()
                if len(assessments) > 1:
                    for assessment in assessments:
                        if len(assessments) > 1:
                            assessment.delete()
            assessments = Attendance.objects.filter(test=test, student=student)
            if len(assessments) == 0:
                assessment = Attendance(
                    test=test, 
                    student=student
                )
                assessment.save()
    return HttpResponseRedirect(reverse("login"))

def fix_assessment(request):
    tests = ProfTest.objects.all()
    for test in tests:
        for student in test.students.all():
            for criterion in test.program.criteria.all():
                assessments = Assessment.objects.filter(test=test, student=student, criterion=criterion)
                if len(assessments) > 1:
                    for assessment in assessments:
                        if assessment.grade not in [0,1,2]:
                            assessment.delete()
                assessments = Assessment.objects.filter(test=test, student=student, criterion=criterion)
                if len(assessments) == 0:
                    assessment = Assessment(
                        test=test, 
                        student=student,
                        criterion=criterion
                    )
                    assessment.save()
            for criterion in test.program.soft_criteria.all():
                assessments = Assessment.objects.filter(test=test, student=student, criterion=criterion)
                if len(assessments) > 1:
                    for assessment in assessments:
                        if assessment.grade not in [0,1,2]:
                            assessment.delete()
                assessments = Assessment.objects.filter(test=test, student=student, criterion=criterion)
                if len(assessments) == 0:
                    assessment = Assessment(
                        test=test, 
                        student=student,
                        criterion=criterion
                    )
                    assessment.save()
    return HttpResponseRedirect(reverse("login"))

def fill_test(request):
    streams = TrainingStream.objects.all()
    for stream in streams:
        for test in stream.tests.all():
            test.students.add(*stream.students.all())
            test.save()
            for student in test.students.all():
                for criterion in test.program.criteria.all():
                    assessment = Assessment(
                        test=test,
                        student=student,
                        criterion=criterion
                    )
                    assessment.save()
                for criterion in test.program.soft_criteria.all():
                    assessment = Assessment(
                        test=test,
                        student=student,
                        criterion=criterion
                    )
                    assessment.save()
                
                attendance = Attendance(
                    test=test,
                    student=student
                )
                attendance.save()

    return HttpResponseRedirect(reverse("login"))

def add_students(request):
    return HttpResponseRedirect(reverse("login"))
    cycles = TrainingCycle.objects.all()
    for cycle in cycles:
        for stream in cycle.streams.all():
            cycle.students.add(*stream.students.all())
        cycle.save()
    return HttpResponseRedirect(reverse("login"))