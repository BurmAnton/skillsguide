import email
import math
from datetime import datetime, timedelta

from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
#Decorators
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

#Models
from .models import Bundle, Stream, TimeSlot
from users.models import User, School, SchoolClass
from education_centers.models import EducationCenter, TrainingProgram, Competence, Workshop


# Create your views here.
def index(request):
    return HttpResponseRedirect(reverse("login"))


@login_required
@csrf_exempt
def create_cycle(request):
    bundles = Bundle.objects.all()
    if request.method == 'POST':
        bundle_id = request.POST["bundle"]
        start_date = datetime.strptime(request.POST["start_date"],"%Y-%m-%d")
        
        any_day = request.POST["any_day"]
        
        if any_day == False:
            schedule_type = 'SDW'
            days_count = 0
            days_of_week
            #Проверяю какие дни выбраны и добавляю их к массиву
            days_of_week = []
            for i in range(1,6):
                try:
                    days_of_week.append(int(request.POST[str(i)]))
                except:
                    pass
        else:
            schedule_type = 'ADW'
            days_count = int(request.POST["days_count"])

        ex_dates = request.POST["dates"]
        start_time = datetime.strptime(request.POST["start_time"], "%H:%M").time()
        group_limit = int(request.POST["group_limit"])
        students_limit = int(request.POST["students_limit"])

        #Получаем массив дней исключений 
        try:
            ex_dates = ex_dates.split(",")
            ex_dates = [datetime.strptime(x,"%d/%m/%y") for x in ex_dates]
        except:
            ex_dates = []

        steams_count = math.ceil(students_limit / group_limit)
        bundle = Bundle.objects.get(id=bundle_id)
        
        for i in range(steams_count):
            stream = Stream(
                bundle=bundle,
                start_date=start_date,
                attendance_limit=group_limit,
                schedule_type=schedule_type
            )
            stream.save()
            slots = 0
            if any_day == False:
                slot_date = start_date
                while slots < steams_count:
                    if slot_date.weekday() in days_of_week and slot_date not in ex_dates:
                        slot = TimeSlot(
                            stream=stream,
                            date=slot_date,
                            time=start_time,
                            week_limit=days_count
                        )
                        slot.save()
                        slots += 1
                    slot_date += timedelta(days=1)
            else:
                slot_date = start_date
                weeks_count = math.ceil(steams_count/days_count)+2
                for week_number in range(weeks_count):
                    while slot_date.weekday() in [5,6]:
                        slot_date += timedelta(days=1)
                    while slot_date.weekday() != 5:
                        if slot_date not in ex_dates:
                            slot = TimeSlot(
                                stream=stream,
                                date=slot_date,
                                time=start_time,
                                week_number=week_number
                            )
                        slot.save()
                        slot_date += timedelta(days=1)
        
        return render(request, "schedule/cycle_form.html", {
            'bundles': bundles,
            'steams_count': steams_count
        })
    
    return render(request, "schedule/cycle_form.html", {
        'bundles': bundles,
    })


@login_required()
def student_profile(request, user_id):
    user = User.objects.get(id=user_id)
    school = user.school

    return render(request, "schedule/student_profile.html",{
        'page_name': 'Личный кабинет',
        'user': user,
        'school': school
    })


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
        if len(timeslot) != 0:
            timeslot = timeslot[0]
        else:
            timeslot = None
        if stream.schedule_type == "SDW":
            stream_slots = TimeSlot.objects.filter(competence=None, stream=stream)
        else:
            weeks_count = TimeSlot.objects.filter(competence=None, stream=stream).aggregate(Max('week_number'))['week_number__max']
            free_weeks = []
            for week_number in range(weeks_count):
                week_slots = TimeSlot.objects.exclude(competence=None).filter(stream=stream, week_number=week_number)
                if len(week_slots) < stream.week_limit:
                    free_weeks.append(week_number)
            stream_slots = TimeSlot.objects.filter(competence=None, stream=stream, week_number__in=free_weeks)
                
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
            school_classes = SchoolClass.objects.filter(school=school, grade_number=i)
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