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
from .models import Attendance, Bundle, Stream, TimeSlot, Assessment
from users.models import DisabilityType, User, School, SchoolClass, SchoolContactPersone, City
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

@login_required
def streams_fill(request, bundle_id):
    if not(request.user.is_staff):
        return HttpResponseRedirect(reverse("login")) 

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
            
    return HttpResponseRedirect(reverse("login")) 

@login_required
def slots_fill(request, bundle_id):
    if request.user.is_staff:
        bundle = get_object_or_404(Bundle, id=bundle_id)
        streams = Stream.objects.filter(bundle=bundle)
        
        for stream in streams: 
            slots = TimeSlot.objects.filter(stream=stream).exclude(competence=None).distinct()
            for slot in slots: 
                slot.participants.add(*stream.participants.all())
                slot.save()
    return HttpResponseRedirect(reverse("login")) 

@login_required
def student_profile(request, user_id):
    user = request.user
    school = user.school

    bundles = Bundle.objects.filter(schools=school).exclude(participants=user)
    available_bundles = []
    for bundle in bundles:
        streams = Stream.objects.filter(bundle=bundle)
        if len(streams) != 0:
            stream = streams[0]
            attendance_limit = stream.attendance_limit * len(streams)
            if len(bundle.participants.all()) < attendance_limit:
                available_bundles.append(bundle)

    slots = TimeSlot.objects.filter(participants=user).order_by('date')
    slots_list = []
    for slot in slots:
        attendance = Attendance.objects.filter(timeslot=slot, user=user)
        if len(attendance) != 0:
            attendance = attendance[0].is_attend
        else:
            attendance = False
        assessments = Assessment.objects.filter(timeslot=slot, user=user)
        assessments_sum = assessments.aggregate(Sum('grade'))['grade__sum']
        slots_list.append([slot,attendance,assessments,assessments_sum])
            
    if len(slots) >= 2:
        upcoming_slots = list(slots.filter(date__gte=date.today()))[:2]
    elif len(slots) != 0:
        upcoming_slots = list(slots.filter(date__gte=date.today()))
    else:
        upcoming_slots = None

    return render(request, "schedule/student_profile.html",{
        'page_name': 'Личный кабинет',
        'user': user,
        'slots': slots_list,
        'upcoming_slots': upcoming_slots,
        'schools': School.objects.all(),
        'disability_types': DisabilityType.objects.all(),
        'choosen_bundles': Bundle.objects.filter(participants=user),
        'choosen_bundles_len': len(Bundle.objects.filter(participants=user)),
        'bundles': available_bundles,
        'bundles_count': len(available_bundles)
    })

@login_required
@csrf_exempt
def choose_bundle(request):
    if request.method == 'POST':
        bundle = Bundle.objects.filter(id=request.POST["bundle_id"])
        if len(bundle) != 0:
            bundle = bundle[0]
            bundle.participants.add(request.user)
            bundle.save()
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
        
        school_class = SchoolClass.objects.filter(
                school=school,
                grade_number=grade_number,
                grade_letter=grade_letter
        )
        if len(school_class) != 0:
            school_class = school_class[0]
        else:
            school_class = SchoolClass(
                school=school,
                grade_number=int(grade_number),
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
            for week_number in range(weeks_count+1):
                week_slots = TimeSlot.objects.exclude(competence=None).filter(stream=stream, week_number=week_number)
                if len(week_slots) < stream.week_limit:
                    free_weeks.add(week_number)
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

#Школа
def school_profile(request, school_id):
    school = get_object_or_404(School, id=school_id)
    students = User.objects.filter(school=school, role='ST')
    slots = TimeSlot.objects.filter(participants__in=students).distinct().order_by('date')
    if len(slots) >= 2:
        upcoming_slots = list(slots.filter(date__gte=date.today()))[:2]
    elif len(slots) == 2:
        upcoming_slots = list(slots.filter(date__gte=date.today()))[0]
    else:
        upcoming_slots = None
    try:
        contact = SchoolContactPersone.objects.get(school=school.id)
    except SchoolContactPersone.DoesNotExist:
        contact = None
    
    return render(request, "schedule/school_profile.html",{
        "cities": City.objects.all(),
        "school": school,
        "slots": [slot.serialize() for slot in slots],
        'upcoming_slots': upcoming_slots,
        "slots_count": len(slots),
        'contact': contact
    })

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

@login_required
@csrf_exempt
def change_school(request):
    if request.method == "POST":
        try:
            school = School.objects.get(id=request.POST["school_id"])
        except School.DoesNotExist:
            return HttpResponseRedirect(reverse("school_profile", args=(school.id,)))
        school.name = request.POST["name"]
        try:
            school.city = City.objects.get(id=request.POST["city"])
        except City.DoesNotExist:
            pass
        school.adress = request.POST["adress"]
        school.save()
        try:
            contact = SchoolContactPersone.objects.get(school=school)
        except SchoolContactPersone.DoesNotExist:
            return HttpResponseRedirect(reverse("school_profile", args=(school.id,)))
        contact.user.phone_number = request.POST["phone"]
        contact.user.email = request.POST["email"]
        contact.user.save()

    return HttpResponseRedirect(reverse("school_profile", args=(school.id,)))