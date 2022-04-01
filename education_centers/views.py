import string
import random

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from education_centers.models import Competence, EducationCenter, Workshop
from schedule.models import TimeSlot
from .forms import ImportDataForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .imports import  slots_import
from users.models import User

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
    education_center = EducationCenter.objects.get(id=request.user.education_centers.id)
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
    education_center = EducationCenter.objects.get(id=request.user.education_centers.id)
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
def trainer_profile(request, trainer_id):
    trainer = get_object_or_404(User, id=trainer_id)

    return render(request, "education_centers/trainer_profile.html",{
        "trainer": trainer,
        "slots": trainer.slots.all(),
    })