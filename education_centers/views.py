import string
import random
from datetime import date

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from education_centers.models import Competence, Criterion, EducationCenter, TrainingProgram, Workshop
from schedule.models import TimeSlot, Assessment, Attendance
from .forms import ImportDataForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .imports import  slots_import
from users.models import User, SchoolContactPersone

# Create your views here.
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
@csrf_exempt
def add_trainer(request):
    message = ""
    if request.method == "POST":
        email = request.POST["email"]
        education_center = EducationCenter.objects.get(id=request.POST["education_center"])
        phone_number = request.POST["phone"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        middle_name = request.POST["middle_name"]
        
        user = User.objects.create_user(email, 'copp8888')
        user.first_name = first_name
        user.middle_name  = middle_name
        user.last_name = last_name
        user.role = 'TCH'
        user.phone_number = phone_number
        user.save()

        education_center.trainers.add(user)
        education_center.save()
        message="Преподаватель добавлен"
    
    education_centers = EducationCenter.objects.filter(contact_person=request.user)
    return render(request, "education_centers/add_trainer.html",{
        "education_centers": education_centers,
        "message": message
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
