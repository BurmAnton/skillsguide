import datetime
import math
import secrets
import string
import random
from datetime import date, timedelta
from django.db import IntegrityError

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from requests import post
import education_centers

from education_centers.models import Competence, Criterion, EducationCenter, TrainingProgram, Workshop, Trainer
from schedule.models import Assessment, Attendance, AvailableDate, Conference, ProfTest, Training, TrainingCycle, TrainingStream
from .forms import ImportDataForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from users.mailing import send_mail

from users.models import DisabilityType, User 
from schools.models import SchoolContactPersone
from regions.models import City, TerAdministration, Address
from . import imports

# Create your views here.
def password_generator():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

@login_required
@csrf_exempt
def add_ed_center(request):
    message = None
    if request.method == 'POST':
        inn = request.POST["INN"]
        duplicates = EducationCenter.objects.filter(inn=inn)
        if len(duplicates) != 0:
            message = "Центр обучения с таким ИНН уже существует!"
        else:
            city_id = request.POST["City"]
            city = City.objects.get(id=city_id)
            street = request.POST["Street"]
            building_number = request.POST["BuildingNumber"]

            address = Address(
                city=city,
                street=street,
                building_number=building_number
            )
            address.save()
            
            email = request.POST["Email"]
            password = password_generator()
            contact_person = User.objects.create_user(email, password)
            contact_person.first_name = request.POST["FirstName"]
            contact_person.middle_name = request.POST["MiddleName"]
            contact_person.last_name = request.POST["LastName"]
            contact_person.phone_number = request.POST["Phone"]
            contact_person.role = 'REC'
            contact_person.save()
            
            name = request.POST["Name"]
            short_name = request.POST["ShortName"]
            is_trains = True
            education_center = EducationCenter(
                inn=inn,
                name=name,
                short_name=short_name,
                is_trains=is_trains,
                address=address,
                contact_person=contact_person
            )
            education_center.save()
            message = "Success"
            
            #Отправляем email+пароль на почту
            subject = 'Данные для входа в личный кабинет skillsguide.ru (проект "Мой выбор")'
            html = f'Здравствуйте, {contact_person.first_name}!<p>Вам предоставлен доступ к платформе http://skillsguide.ru/ (проект "Мой выбор"), как представителю центра обучения ({education_center.name}).</p> <p><br><b>Логин:</b> {contact_person.email}<br><b>Пароль:</b> {password}</p><br><br>Это автоматическое письмо на него не нужно отвечать.'
            text = f'Здравствуйте!\n Здравствуйте, {contact_person.first_name}! \nВам предоставлен доступ к платформе http://skillsguide.ru/ (проект "Мой выбор"), как представителю центра обучения ({education_center.name}).\nЛогин: {contact_person.email}\nПароль: {password} \n\nЭто автоматическое письмо на него не нужно отвечать.'
            to_name = f"{contact_person.first_name} {contact_person.last_name}"
            to_email = email
            send_mail(subject, html, text, to_name, to_email)

    cities = City.objects.all()
    
    return render(request, 'education_centers/add_ed_center.html', {
        'cities': cities,
        'message': message
    })

@login_required
@csrf_exempt
def import_ed_centers(request):
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.ed_centers(form)
            message = data[0]
            return render(request, 'education_centers/import_ed_centers.html', {
                'form': ImportDataForm(),
                'message': message,
                'data': data
            })
        else:
            data = form.errors
            message = "IndexError"

    return render(request, 'education_centers/import_ed_centers.html', {
        'form' : ImportDataForm()
    })

@login_required
@csrf_exempt
def ed_center_dashboard(request, ed_center_id, message=None):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    if request.user != ed_center.contact_person and request.user.is_superuser == False:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        city_id = request.POST["City"]
        city = City.objects.get(id=city_id)
        street = request.POST["Street"]
        building_number = request.POST["BuildingNumber"]

        address = Address(
            city=city,
            street=street,
            building_number=building_number
        )
        address.save()
        ed_center.address = address
        
        contact_person = ed_center.contact_person
        contact_person.email = request.POST["Email"]
        contact_person.first_name = request.POST["FirstName"]
        contact_person.middle_name = request.POST["MiddleName"]
        contact_person.last_name = request.POST["LastName"]
        contact_person.phone_number = request.POST["Phone"]
        contact_person.save()
        
        ed_center.name = request.POST["Name"]
        ed_center.short_name = request.POST["ShortName"]
        ed_center.is_trains = True
        ed_center.save()
    
    two_weeks = datetime.datetime.today() + timedelta(14)
    tests = ProfTest.objects.filter(
        ed_center=ed_center, 
        date__gte=datetime.datetime.today(), 
        date__lte=two_weeks
        ).order_by('date', 'start_time')

    return render(request, 'education_centers/ed_center.html', {
        'ed_center' : ed_center,
        'tests': tests,
        'competencies': Competence.objects.all(),
        'programs': TrainingProgram.objects.filter(education_center=ed_center),
        'trainers': Trainer.objects.filter(education_center=ed_center),
        'disability_types': DisabilityType.objects.all(),
        'cities': City.objects.all(),
        'workshops': Workshop.objects.filter(education_center=ed_center),
        'conferences': Conference.objects.filter(education_center=ed_center),
        'message': message
    })

@login_required
@csrf_exempt
def tests_list(request, ed_center_id):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    tests = ProfTest.objects.filter(
        ed_center=ed_center, 
        date__lte=datetime.datetime.today()
    ).order_by('date', 'start_time')

    return render(request, 'education_centers/tests_list.html', {
        'ed_center' : ed_center,
        'tests': tests,
    })

@login_required
@csrf_exempt
def test_assessment(request, ed_center_id, test_id):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    test = get_object_or_404(ProfTest, id=test_id)
    if request.method == "POST":
        for attendance in test.attendance.all():
            try:
                is_attend = request.POST[f'attendance_{attendance.student.id}']
                is_attend = True
            except: 
                is_attend = False
            attendance.is_attend = is_attend
            attendance.save()
            if is_attend:
                for assessment in test.assessment.filter(student=attendance.student):
                    grade = request.POST[f'assessment_{assessment.id}']
                    if grade != "—":
                        assessment.grade = int(grade)
                        assessment.save()

    return render(request, 'education_centers/test_assessment.html', {
        'ed_center' : ed_center,
        'test': test
    })

@login_required
@csrf_exempt
def add_program(request):
    if request.method == "POST":
        name = request.POST["name"]
        short_desc = request.POST["short_desc"]
        program_link = request.POST["program_link"]
        program_type = request.POST["program_type"]
        disability_types = request.POST.getlist("disability_types")
        if 'edit-program' in request.POST:
            program = get_object_or_404(TrainingProgram, id=request.POST["program_id"])
            program.name = name
            program.short_desciption = short_desc
            program.program_link = program_link
            program.program_type = program_type
            program.status = 'CHCK'
            program.save()
            for criterion in program.criteria.all():
                criterion.name = request.POST[f'CriterionName{criterion.id}']
                criterion.description = request.POST[f'CriterionDesc{criterion.id}']
                criterion.save()
            soft_criteria = Criterion.objects.filter(skill_type="SFT")
            program.soft_criteria.add(*soft_criteria)
            program.save()
        else:
            education_center = request.POST["education_center"]
            education_center = get_object_or_404(EducationCenter, id=education_center)
            program = TrainingProgram(
                name=name,
                short_description=short_desc,
                program_link=program_link,
                program_type=program_type,
                education_center=education_center,
            )
            program.save()
            criteria = Criterion.objects.filter(skill_type="SFT")
            program.soft_criteria.add(*criteria)
            if len(program.criteria.all()) == 0:
                for i in range(1,6):
                    criterion = Criterion(
                        name=request.POST[f'CriterionName{i}'],
                        description=request.POST[f'CriterionDesc{i}'],
                        program=program,
                        skill_type='HRD',
                        grading_system=2
                    )
                    criterion.save()
        program.disability_types.add(*disability_types)
        program.save()

    return HttpResponseRedirect(reverse("login"))

def password_generator():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

@login_required
@csrf_exempt
def add_trainer(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = password_generator()
        try:
            user = User.objects.create_user(email, password)
        except IntegrityError:
            message = "userDuplicate"
            education_center = request.POST["education_center"]
            education_center = get_object_or_404(EducationCenter, id=education_center)
            return HttpResponseRedirect(reverse('ed_center_dashboard', args=(education_center.id, message)))
        user.first_name = request.POST["name"]
        user.middle_name = request.POST["middle_name"]
        user.last_name = request.POST["last_name"]
        user.phone_number = request.POST["phone"]
        user.role = 'INTS'
        user.save()

        position = request.POST["position"]
        education_center = request.POST["education_center"]
        education_center = get_object_or_404(EducationCenter, id=education_center)
        trainer = Trainer(
            user=user,
            position=position,
            education_center=education_center
        )
        trainer.save()
        message = "userOk"      
    return HttpResponseRedirect(reverse('ed_center_dashboard', args=(education_center.id, message)))

@login_required
@csrf_exempt
def add_workshop(request):
    if request.method == "POST":
        education_center = request.POST["education_center"]
        education_center = get_object_or_404(EducationCenter, id=education_center)
        
        city = request.POST["city"]
        city = get_object_or_404(City, id=city)
        street = request.POST["street"]
        building_number = request.POST["building_number"]
        floor = int(request.POST["floor"])
        apartment = request.POST["apartment"]
        address, is_new = Address.objects.get_or_create(
            city=city,
            street=street,
            building_number=building_number,
            floor=floor,
            apartment=apartment
        )
        description = request.POST["description"]
        competence = request.POST["competence"]
        competence= get_object_or_404(Competence, id=competence)
        if 'edit-program' in request.POST:
            workshop_id = request.POST["workshop"]
            workshop = get_object_or_404(Workshop, id=workshop_id)
            workshop.education_center=education_center
            workshop.competence=competence
            workshop.adress=address
            workshop.description=description
            workshop.save()
            message = "WorkshopEdited"
        else:
            workshop = Workshop(
                education_center=education_center,
                competence=competence,
                adress=address,
                description=description
            )
            workshop.save()
            message = "WorkshopAdded"
    return HttpResponseRedirect(reverse('ed_center_dashboard', args=(education_center.id, message)))

@login_required
@csrf_exempt
def add_conference(request):
    message = ""
    if request.method == "POST":
        education_center = request.POST["education_center"]
        education_center = get_object_or_404(EducationCenter, id=education_center)
        
        name = request.POST["name"]
        invite_link = request.POST["invite_link"]
        Identifier = request.POST["Identifier"]
        access_code = request.POST["access_code"]
        instruction = request.POST["instruction"]
        if 'edit-conference' in request.POST:
            conference_id = request.POST["conference"]
            conference = get_object_or_404(Conference, id=conference_id)
            conference.invite_link=invite_link
            conference.Identifier=Identifier
            conference.access_code=access_code
            conference.instruction=instruction
            conference.save()
            message = "ConferenceEdited"
        else:   
            conference = Conference(
                name=name,
                invite_link=invite_link,
                access_code=access_code,
                Identifier=Identifier,
                instruction=instruction,
                education_center=education_center
            )
            conference.save()
            message = "ConferenceAdded"
    return HttpResponseRedirect(reverse('ed_center_dashboard', args=(education_center.id, message)))

@login_required
@csrf_exempt
def import_programs(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = slots_import(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "education_centers/import.html",{
            'form': form,
            'message': message
        })

    form = ImportDataForm()
    return render(request, "education_centers/import.html",{
        'form': form
    })

@login_required
def trainers_list(request):
    if request.user.role != 'CO':
        return HttpResponseRedirect(reverse("login"))
    education_center = request.user.education_center
    return render(request, "education_centers/trainers_list.html",{
        "education_center": education_center,
        "trainers": education_center.trainers.all()
    })

@login_required
def workshops_list(request):
    if request.user.role != 'CO':
        return HttpResponseRedirect(reverse("login"))
    education_center = EducationCenter.objects.get(id=request.user.education_center.id)
    return render(request, "education_centers/workshops_list.html",{
        "education_center": education_center,
        "workshops": education_center.workshops.all()
    })

@login_required
@csrf_exempt
def program_schedule(request, ed_center_id, program_id):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    program = get_object_or_404(TrainingProgram, id=program_id)
    tests = ProfTest.objects.filter(ed_center=ed_center, program=program)
    message = ""
    if request.method == "POST":
        for test in tests:
            test_date = request.POST[f'test{test.id}_date']
            if test_date == "None":
                test.date = None
            elif test_date.isnumeric():
                if test.date != None:
                    previous_date = AvailableDate.objects.get(
                        stream=test.stream,
                        date=test.date
                    )
                    previous_date.busy = False
                    previous_date.save()
                available_date = get_object_or_404(AvailableDate, id=test_date)
                test.date = available_date.date
                available_date.busy = True
                available_date.save()
                if test.stream.cycle.is_any_day:
                    busy_dates = AvailableDate.objects.filter(
                        stream=test.stream,
                        busy=True,
                        week_number=available_date.week_number
                    )
                    free_dates = AvailableDate.objects.filter(
                        stream=test.stream, 
                        busy=False,  
                        week_number=available_date.week_number)
                    if len(busy_dates) >= test.stream.cycle.days_per_week:
                        for date in free_dates:
                            date.is_unavailable = True
                            date.save()
                    else:
                        for date in free_dates:
                            date.is_unavailable = False
                            date.save()
            test.start_time = request.POST[f'test{test.id}_start_time']
            trainer_id = request.POST[f'test{test.id}_trainer']
            test.trainer = get_object_or_404(Trainer, id=trainer_id)
            try:
                is_online = request.POST[f'test{test.id}_is_online']
                is_online = True
            except:
                is_online = False
            conference = request.POST[f'test{test.id}_conference']
            workshop = request.POST[f'test{test.id}_workshop']
            if is_online and conference != 'None':
                conference = get_object_or_404(Conference, id=conference)
                test.conference = conference
                test.workshop = None
            elif workshop != 'None':
                workshop = get_object_or_404(Workshop, id=workshop)
                test.workshop = workshop
                test.conference = None
            else:
                test.workshop = None
                test.conference = None
            test.save()
        message = "TestsAdded"
    return render(request, "education_centers/program_schedule.html",{
        "ed_center": ed_center,
        "program": program,
        "workshops": ed_center.workshops.all(),
        "conferences": ed_center.conferences.all(),
        "tests": tests,
        "message": message
    })

#Преродаватель
def trainer_profile(request, trainer_id, page_number):
    trainer = get_object_or_404(User, id=trainer_id)
    if trainer.role == 'CO':
        slots = TimeSlot.objects.filter(education_center=trainer.education_center).exclude(participants=None).order_by('date')
    else:
        slots = TimeSlot.objects.filter(trainer=trainer).exclude(participants=None).order_by('date')
    if len(slots) >= 2:
        upcoming_slots = list(slots.filter(date__gte=date.today()))[:2]
    elif len(slots) == 2:
        upcoming_slots = list(slots.filter(date__gte=date.today()))[0]
    else:
        upcoming_slots = None
     
    slots = Paginator(slots, 12)
    slots_page = slots.get_page(page_number)
    pages = slots.num_pages

    previous_page_number = page_number - 1
    if previous_page_number <= 0:
        previous_page_number = None
    next_page_number = page_number + 1
    if next_page_number > slots.num_pages:
        next_page_number = None

    return render(request, "education_centers/trainer_profile.html",{
        "trainer": trainer,
        "slots": [slot.serialize() for slot in slots_page],
        "page_number": page_number,
        "previous_page_number": previous_page_number,
        "next_page_number": next_page_number,
        "page_list": range(1,slots.num_pages+1),
        "num_page": slots.num_pages,
        'upcoming_slots': upcoming_slots
    })

@login_required
@csrf_exempt
def add_zoom_link(request):
    if request.method == "POST":
        slot = get_object_or_404(TimeSlot, id=request.POST["slot_id"])
        link = request.POST["link"]
        instruction = request.POST["instruction"]

        slot.zoom_link = link
        slot.zoom_instruction = instruction
        slot.save()
    
    return HttpResponseRedirect(reverse("trainer_profile", args=(request.user.id,)))


@login_required
@csrf_exempt
def set_assessment(request):
    if request.method == "POST":
        slot = get_object_or_404(TimeSlot, id=request.POST["slot_id"])
        for user in slot.participants.all():
            attendance = get_object_or_404(Attendance, user=user, timeslot=slot)
            try:
                attendance_id=request.POST[f"{slot.id}_{user.id}_attendance"]
                attendance.is_attend = True
            except:
                attendance.is_attend = False
            attendance.save()
            for assessment in slot.assessment.filter(user=user):
                grade=request.POST[f"{slot.id}_{user.id}_{assessment.id}"]
                if grade != "–":
                    assessment.grade = int(grade)
                    assessment.save()

    return HttpResponseRedirect(reverse("trainer_profile", args=(request.user.id,1)))
