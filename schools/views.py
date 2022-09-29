import secrets
import string

from email import message
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from users.models import User
from regions.models import City, TerAdministration, Address
from .models import Grade, School, SchoolContactPersone, SchoolStudent

from education_centers.forms import ImportDataForm
from users.mailing import send_mail
from . import imports

#ЛК школы
def school_profile(request, school_id):
    school = get_object_or_404(School, id=school_id)
    try:
        contact = SchoolContactPersone.objects.get(school=school.id)
    except SchoolContactPersone.DoesNotExist:
        contact = None
    
    students_count = len(school.students.all())
    grades = Grade.objects.filter(school=school, is_graduated=False).annotate(students_count = Count('students'))
    
    return render(request, "schools/school_profile.html",{
        "cities": City.objects.all(),
        "school": school,
        "students_count": students_count,
        "school_students": school.students.all(),
        'grades': grades,
        'contact': contact
    })

# Изменение данных школы/конт. лица
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

def password_generator():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

# Добавление школ
@csrf_exempt
@login_required
def add_school(request):
    message = None
    if request.method == 'POST':
        inn = request.POST["INN"]
        check_inn = School.objects.filter(inn=inn)
        if len(check_inn) != 0:
            message = "Школа с таким ИНН уже существует!"
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
            ter_admin_id = request.POST["TerAdmin"]
            ter_admin = TerAdministration.objects.get(id=ter_admin_id)
            school_name = request.POST["SchoolName"]
            school = School(
                inn=inn,
                name=school_name,
                ter_administration=ter_admin,
                address=address
            )
            school.save()
            email = request.POST["Email"]
            password = password_generator()
            user = User.objects.create_user(email, password)
            user.first_name = request.POST["FirstName"]
            user.middle_name = request.POST["MiddleName"]
            user.last_name = request.POST["LastName"]
            user.phone_number = request.POST["Phone"]
            user.role = 'RSC'
            user.save()
            contact = SchoolContactPersone(
                user=user,
                school=school
            )
            contact.save()
            message = "Success"
            
            #Отправляем email+пароль на почту
            subject = 'Данные для входа в личный кабинет skillsguide.ru'
            html = f'Здравствуйте, {user.first_name}!<p>Вам предоставлен доступ к платформе http://skillsguide.ru/ (проект "Мой выбор"), как представителю школы "{school.name}".</p> <p><br><b>Логин:</b> {user.email}<br><b>Пароль:</b> {password}</p><br><br>Это автоматическое письмо на него не нужно отвечать.'
            text = f'Здравствуйте!\n Здравствуйте, {user.first_name}! \nВам предоставлен доступ к платформе http://skillsguide.ru/ (проект "Мой выбор"), как представителю школы "{school.name}".\nЛогин: {user.email}\nПароль: {password} \n\nЭто автоматическое письмо на него не нужно отвечать.'
            to_name = f"{user.first_name} {user.last_name}"
            to_email = email
            send_mail(subject, html, text, to_name, to_email)

    cities = City.objects.all()
    ter_admins = TerAdministration.objects.all()
    
    return render(request, 'schools/add_school.html', {
        'cities': cities,
        'ter_admins': ter_admins,
        'message': message
    })

#Импорт школ
#[True, schools_count, problems, dublicates]
@csrf_exempt
@login_required
def import_schools(request):
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.schools(form)
            message = data[0]
            return render(request, 'schools/import_schools.html', {
                'form': ImportDataForm(),
                'message': message,
                'data': data
            })
        else:
            data = form.errors
            message = "IndexError"

    return render(request, 'schools/import_schools.html', {
        'form' : ImportDataForm()
    })
