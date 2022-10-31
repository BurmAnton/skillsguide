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
from .models import Attendance, Assessment, TrainingBundle, TrainingCycle, FieldOfActivity, TrainingStream
from users.models import DisabilityType, User
from regions.models import City
from schools.models import School, Grade, SchoolContactPersone, SchoolStudent
from education_centers.models import EducationCenter, TrainingProgram, Competence, Workshop, Criterion


# Create your views here.
def index(request):
    return HttpResponseRedirect(reverse("login"))

@login_required
def student_profile(request, user_id):
    user = request.user
    student = get_object_or_404(SchoolStudent, user=user)
    school = student.school

    return render(request, "schedule/student_profile.html",{
        'page_name': 'Личный кабинет',
        'user': user,
        'student': student,
        'school': school
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


@login_required
@csrf_exempt
def create_cycle(request):
    if request.method == 'POST':
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

        start_date = datetime.strptime(request.POST["start_date"],"%Y-%m-%d")
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
        for i in range(steams_count):
            stream = TrainingStream(
                cycle=cycle,
                students_limit=group_limit,
            )
            stream.save()
            slots = 0
            #№if any_day == False:
            #    slot_date = start_date
            #    while slots < steams_count:
            #        if slot_date.weekday() in days_of_week and slot_date not in ex_dates:
             #           slot = TimeSlot(
              #              stream=stream,
               #             date=slot_date,
                #            time=start_time,
                 #           week_limit=days_count
                  #      )
                   #     slot.save()
                    #    slots += 1
                    #slot_date += timedelta(days=1)
            #else:
             #   slot_date = start_date
              #  weeks_count = math.ceil(steams_count/days_count)+2
               # for week_number in range(weeks_count):
                #    while slot_date.weekday() in [5,6]:
                 #       slot_date += timedelta(days=1)
                  #  while slot_date.weekday() != 5:
                   #     if slot_date not in ex_dates:
                    #        slot = TimeSlot(
                     #           stream=stream,
                      #          date=slot_date,
                       #         time=start_time,
                        #        week_number=week_number
                         #   )
                        #slot.save()
                        #slot_date += timedelta(days=1)
        
        return HttpResponseRedirect(reverse("bundles_list")) 
    
    return HttpResponseRedirect(reverse("login")) 

def streams_fill(bundle_id):
    bundle = get_object_or_404(Bundle, id=bundle_id)
    schools = School.objects.filter(bundles=bundle)
    users = User.objects.filter(school__in=schools, role='ST')
    for user in users:
        user.bundles.add(bundle)
        user.save()
    if len(schools) != 0:
        streams = Stream.objects.filter(bundle=bundle)
        #Первый цикл – наполняем потоки только цельными классами
        #Второй цикл – распределяем остальных
        for cycle in range(1,3):
            for stream in streams:
                if len(User.objects.filter(school__in=schools, streams=None, role='ST')) != 0:
                    school_number = 0
                    while stream.attendance_limit != len(stream.participants.all()):
                        for school_class in schools[school_number].classes.all():
                            current_limit = stream.attendance_limit - len(stream.participants.all())
                            if current_limit == 0:
                                break
                            class_students = User.objects.filter(school=schools[school_number], school_class=school_class, streams=None, role='ST')
                            if len(class_students) <= current_limit:
                                stream.participants.add(*class_students)
                            elif cycle == 2:
                                stream.participants.add(*class_students[0:current_limit-1])
                            stream.save()
                        if school_number+1 >= len(schools):
                            break
                        else:
                            school_number += 1
                else:
                    break

def slots_fill(bundle_id):
    bundle = get_object_or_404(Bundle, id=bundle_id)
    streams = Stream.objects.filter(bundle=bundle)
    
    for stream in streams: 
        slots = TimeSlot.objects.filter(stream=stream).exclude(competence=None).distinct()
        for slot in slots: 
            slot.participants.add(*stream.participants.all())
            slot.save()
    return HttpResponseRedirect(reverse("login")) 


def add_assesment_all():
    programs = TrainingProgram.objects.all()
    soft_skills = Criterion.objects.filter(skill_type='SFT')
    for skill in soft_skills:
        skill.programs.add(*programs)
        skill.save()
    slots = TimeSlot.objects.exclude(program=None).distinct()
    for slot in slots:
        for participant in slot.participants.all():
            attendance = Attendance.objects.filter(user=participant,timeslot=slot)
            if len(attendance) == 0:
                attendance = Attendance(
                    timeslot=slot,
                    user=participant,
                )
                attendance.save()
            for criterion in slot.program.criteria.all():
                assessment = Assessment.objects.filter(user=participant,timeslot=slot, criterion=criterion)
                if len(assessment) == 0:
                    assessment = Assessment(
                        timeslot=slot,
                        criterion=criterion,
                        user=participant,
                    )
                    assessment.save()

@login_required
@csrf_exempt
def choose_bundle(request):
    if request.method == 'POST':
        bundle = Bundle.objects.filter(id=request.POST["bundle_id"])
        if len(bundle) != 0:
            bundle = bundle[0]
            bundle.participants.add(request.user)
            bundle.save()
            streams_fill(bundle.id)
            slots_fill(bundle.id)
            add_assesment_all()
            message = "Registration successful"
        else:
            message = "Bundle doesn't exist"
        
    return HttpResponseRedirect(reverse("login")) 


@login_required
@csrf_exempt
def change_profile_student(request):
    if request.method == "POST":
        user = request.user

        user.email = request.POST["email"]
        user.email = request.POST["email"]
        user.phone_number = request.POST["phone"]
        user.first_name = request.POST['name']
        user.last_name = request.POST['last_name']
        user.middle_name = request.POST['middle_name']
        user.birthday = request.POST['birthday']
        school_id = request.POST['school']
        school = School.objects.get(id=school_id)
        user.school = school
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
            user.disability_type = DisabilityType.objects.get(id=disability_type)
        else:
            user.disability_type = None
        
        school_class = Grade.objects.filter(
                school=school,
                grade=grade_number,
                grade_letter=grade_letter
        )
        if len(school_class) != 0:
            school_class = school_class[0]
        else:
            school_class = Grade(
                school=school,
                grade=int(grade_number),
                grade_letter=grade_letter.upper()
            )
            school_class.save()
        user.school_class = school_class
        user.save()
    return HttpResponseRedirect(reverse("login")) 


@login_required
@csrf_exempt
def competence_schedule(request, ed_center_id, bundle_id, competence_id):
    if request.method == 'POST':
        row_count = int(request.POST["row_count"])
        for row in range(row_count):
            stream = Stream.objects.get(id=request.POST[f"id{row}"])
            program = TrainingProgram.objects.get(id=request.POST[f"program{row}"])
            start_time = datetime.strptime(request.POST[f"start_time{row}"], "%H:%M").time()
            trainer = User.objects.get(id=request.POST[f"trainer{row}"])
            previous_slots = TimeSlot.objects.filter(competence=program.competence, stream=stream)
            for slot in previous_slots:
                slot.program = None
                slot.competence = None
                slot.trainer = None
                slot.online = False
                slot.workshop = None
                slot.education_center = None
                slot.save()
                
            slot = TimeSlot.objects.get(id=request.POST[f"date{row}"])
            slot.program = program
            slot.competence = program.competence
            slot.trainer = trainer
            slot.time = start_time
            slot.education_center = program.education_center
            if request.POST[f"workshop{row}"] == 'online':
                slot.online = True
                slot.workshop = None
            else:
                slot.online = False
                workshop = Workshop.objects.get(id=request.POST[f"workshop{row}"])
                slot.workshop = workshop
            slot.save()

    edu_center = EducationCenter.objects.get(id=ed_center_id)
    bundle = Bundle.objects.get(id=bundle_id)
    competence = Competence.objects.get(id=competence_id)

    programs = TrainingProgram.objects.filter(bundles=bundle, competence=competence)
    workshops = Workshop.objects.filter(competence=competence, education_center=edu_center)

    streams = []
    row_count = 0
    for stream in Stream.objects.filter(bundle=bundle):
        timeslot = TimeSlot.objects.filter(competence=competence, stream=stream)
        free_weeks = set()
        if len(timeslot) != 0:
            timeslot = timeslot[0]
            free_weeks.add(timeslot.week_number)
        else:
            timeslot = None
        if stream.schedule_type == "SDW":
            stream_slots = TimeSlot.objects.filter(competence=None, stream=stream)
        else:
            weeks_count = TimeSlot.objects.filter(competence=None, stream=stream).aggregate(Max('week_number'))['week_number__max']
            if weeks_count is not None:
                for week_number in range(weeks_count+1):
                    week_slots = TimeSlot.objects.exclude(competence=None).filter(stream=stream, week_number=week_number)
                    if len(week_slots) < stream.week_limit:
                        free_weeks.add(week_number)
                stream_slots = TimeSlot.objects.filter(competence=None, stream=stream, week_number__in=free_weeks)
            else:
                stream_slots = None
        streams.append([stream, stream_slots, row_count, timeslot])
        row_count += 1

    return render(request, 'schedule/competence_schedule.html', {
        "edu_center": edu_center,
        "trainers": edu_center.trainers.all(),
        "bundle": bundle,
        "competence": competence,
        "programs": programs,
        "streams": streams,
        "row_count": row_count,
        "workshops": workshops
    })


@login_required
def bundles(request, ed_center_id):
    ed_center = EducationCenter.objects.get(id=ed_center_id)
    bundles = Bundle.objects.filter(edu_centers=ed_center)
    bundles_list = []
    for bundle in bundles:
        programs = TrainingProgram.objects.filter(bundles=bundle, education_center=ed_center)
        groups = Stream.objects.filter(bundle=bundle)
        bundles_list.append([bundle,  len(groups), len(programs)])

    return render(request, 'schedule/bundles.html', {
        "ed_center": ed_center,
        "bundles": bundles_list
    })


@login_required
def competencies(request, ed_center_id, bundle_id):
    ed_center = EducationCenter.objects.get(id=ed_center_id)
    bundle = Bundle.objects.get(id=bundle_id)
    programs = TrainingProgram.objects.filter(bundles=bundle, education_center=ed_center)
    competencies = Competence.objects.filter(bundles=bundle, programs__in=programs)
    competencies_list = []
    for competence in competencies:
        comp_programs = programs.filter(competence=competence)
        streams = Stream.objects.filter(bundle=bundle)
        slots = TimeSlot.objects.filter(competence=competence, stream__in=streams)
        if len(slots) == 0:
            status = "Не заполненно"
        elif len(slots) == len(streams):
            status = "Заполненно"
        else:
            status = "Заполненно частично"
        competencies_list.append([competence, len(comp_programs), len(streams), len(slots), status])
    return render(request, 'schedule/competencies.html', {
        "ed_center": ed_center,
        "bundle": bundle,
        "competencies": competencies_list
    })


def student_dashboard(request):
    schools = School.objects.all()

    schools_list = []
    grades = [0,0,0,0,0,0]
    count_students = 0
    start_user = User.objects.get(email='leila12082006@gmail.com')
    for school in schools:
        school_list = []
        school_list.append(school)
        for i in range(6,12):
            school_classes = Grade.objects.filter(school=school, grade_number=i)
            school_students_count = 0
            if len(school_classes) != 0:
                for school_class in school_classes:
                    school_students_count += len(User.objects.filter(school_class=school_class, date_joined__gte=start_user.date_joined))
                grades[i-6] += school_students_count
                count_students += school_students_count
                school_list.append(school_students_count)
            else:
                school_list.append(0)
        school_list.append(len(User.objects.filter(school=school, date_joined__gte=start_user.date_joined)))
        schools_list.append(school_list)
    
    return render(request, 'schedule/dashboard_students.html', {
        "schools_list": schools_list,
        "grades": grades,
        "count_students": count_students
    })

#Удаление студента со слота
@login_required
@csrf_exempt
def student_dismissal(request):
    if request.method == "POST":
        try:
            school = School.objects.get(id=request.POST["school_id"])
            participant = User.objects.get(id=request.POST["participant_id"])
            slot = TimeSlot.objects.get(id=request.POST["slot_id"])
        except SchoolContactPersone.DoesNotExist:
            return HttpResponseRedirect(reverse("school_profile", args=(school.id,)))
        slot.participants.remove(participant)
        slot.save()
    return HttpResponseRedirect(reverse("school_profile", args=(school.id,)))