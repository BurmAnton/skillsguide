import secrets
import string
import random
from datetime import date

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from requests import post
import education_centers

from education_centers.models import Competence, Criterion, EducationCenter, TrainingProgram, Workshop, Trainer
from schedule.models import TimeSlot, Assessment, Attendance
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
def ed_center_dashboard(request, ed_center_id):
    ed_center = get_object_or_404(EducationCenter, id=ed_center_id)
    if request.user != ed_center.contact_person:
        return HttpResponseRedirect(reverse("login"))


    return render(request, 'education_centers/ed_center.html', {
        'ed_center' : ed_center,
        'programs': TrainingProgram.objects.filter(education_center=ed_center),
        'trainers': Trainer.objects.filter(education_center=ed_center),
        'disability_types': DisabilityType.objects.all()
    })

@login_required
@csrf_exempt
def add_program(request):
    if request.method == "POST":
        name = request.POST["name"]
        short_desc = request.POST["short_desc"]
        program_link = request.POST["program_link"]
        program_type = request.POST["program_type"]
        education_center = request.POST["education_center"]
        education_center = get_object_or_404(EducationCenter, id=education_center)
        disability_types = request.POST.getlist("disability_types")

        program = TrainingProgram(
            name=name,
            short_description=short_desc,
            program_link=program_link,
            program_type=program_type,
            education_center=education_center,
        )
        program.save()
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
        user = User.objects.create_user(email, password)
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
    return HttpResponseRedirect(reverse("login"))

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
def add_workshop(request):
    message = ""
    if request.method == "POST":
        adress = request.POST["adress"]
        education_center = EducationCenter.objects.get(id=request.POST["education_center"])
        competence = Competence.objects.get(id=request.POST["competence"]) 
        description = request.POST["description"]
        
        workshop = Workshop(
            adress=adress,
            education_center=education_center,
            competence=competence,
            description=description
        )
        workshop.save()
        message="Мастерская добавлена"
    
    education_centers = EducationCenter.objects.filter(contact_person=request.user)
    return render(request, "education_centers/add_workshop.html",{
        "education_centers": education_centers,
        "competencies": Competence.objects.all(),
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
