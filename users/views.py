import string
import random
import json

from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
#Decorators
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
#Models
from users.models import User, DisabilityType, School, SchoolClass
from schedule.models import Bundle, EducationCenter

from education_centers.forms import ImportDataForm
from .imports import students_import

from pysendpulse.pysendpulse import PySendPulse
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


# Create your views here.
@csrf_exempt
def login(request):
    message = None
    if request.user.is_authenticated:
        if len(User.objects.filter(role="ST", email=request.user.email)) != 0:
            return HttpResponseRedirect(reverse('student_profile', args=(request.user.id,)))
        elif len(User.objects.filter(role="COR", email=request.user.email)) != 0:
            user = User.objects.filter(email=request.user.email)
            school = School.objects.filter(school_coordinators=user[0].id)
            #return HttpResponseRedirect(reverse("school_dash", args=(school[0].id,)))
        elif len(User.objects.filter(role="CO", email=request.user.email)) != 0:
            edu_center = EducationCenter.objects.filter(contact_person=request.user)
            if len(edu_center) != 0:
                return HttpResponseRedirect(reverse("bundles", args=(edu_center[0].id,)))
        elif request.user.is_staff:
            return HttpResponseRedirect(reverse("create_cycle"))
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse("login"))
        else:
            message = "Неверный логин и/или пароль."

    schools = School.objects.all()
    cities = set()
    for school in schools:
        cities.add(school.city) 
    return render(request, "user/login.html", {
        "message": message,
        "page_name": "ЦОПП СО | Авторизация",
        'schools': schools,
        'cities': cities,
        'disability_types': DisabilityType.objects.all()
    })

@login_required
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect(reverse("login"))

def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def mailing():
    REST_API_ID = 'e071900fe5ab9aa6dd4dec2f42160ead'
    REST_API_SECRET = '7e82daa1ccfd678487a894b3e3487967'
    TOKEN_STORAGE = 'memcached'
    MEMCACHED_HOST = '127.0.0.1:11211'
    SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
    return SPApiProxy


@login_required
@csrf_exempt
def mailing_form(request):
    message = ""
    if request.method == "POST":
        bundle = Bundle.objects.get(id=request.POST['bundle'])
        schools = School.objects.filter(bundles=bundle)
        users = User.objects.filter(school__in=schools)
        
        for user in users:
            text = request.POST['text']
            html = text
            email = {
                    'subject': request.POST['subject'],
                    'html': html,
                    'text': text,
                    'from': {'name': 'ЦОПП СО', 'email': 'bvb@copp63.ru'},
                    'to': [
                        {
                            'name': f"{user.first_name} {user.last_name}", 
                            'email': user.email
                        }
                    ],
                }
            SPApiProxy = mailing()
            SPApiProxy.smtp_send_mail(email)
        message = "OK"

    return render(request, "user/mailing_form.html", {
        'bundles': Bundle.objects.all(),
        'message': message
    })


@csrf_exempt
def password_recovery(request, step):
    if request.method == "POST":
        if step == 1:
            data = json.loads(request.body)
            email = data.get("email", "")
            user = User.objects.filter(email=email)
            if len(user) != 0:
                user = user[0]
                code = code_generator()
                user.code = code
                user.save()
                email = {
                    'subject': 'Востановление пароля skillsguide.ru',
                    'html': f'Здравствуйте!<p>Вы получили это письмо потому, что вы (либо кто-то, выдающий себя за вас) попросили выслать новый пароль к вашей учётной записи на сайте http://skillsguide.ru/. <br> Если вы не просили выслать пароль, то не обращайте внимания на это письмо. <br> Код подтверждения для смены пароля: {code} <br> Это автоматическое письмо на него не нужно отвечать.</p>',
                    'text': f'Здравствуйте!\n Вы получили это письмо потому, что вы (либо кто-то, выдающий себя за вас) попросили выслать новый пароль к вашей учётной записи на сайте http://skillsguide.ru/. \n Если вы не просили выслать пароль, то не обращайте внимания на это письмо. \n Код подтверждения для смены пароля: {code} \n Это автоматическое письмо на него не нужно отвечать.',
                    'from': {'name': 'ЦОПП СО', 'email': 'bvb@copp63.ru'},
                    'to': [
                        {'name': "f{user.first_name} {user.last_name}", 'email': email}
                    ],
                }
                SPApiProxy = mailing()
                SPApiProxy.smtp_send_mail(email)
                return JsonResponse({"message": "Email exist"}, status=201)
            return JsonResponse({"message": "Email not found"}, status=201)
        if step == 2:
            data = json.loads(request.body)
            email = data.get("email", "")
            code = data.get("code", "")
            user = User.objects.get(email=email)
            if user.code == code:
                return JsonResponse({"message": "Code matches"}, status=201)
            return JsonResponse({"message": "Code not matches"}, status=201)
        if step == 3:
            data = json.loads(request.body)
            email = data.get("email", "")
            password = data.get("password", "")
            confirmation = data.get("confirmation", "")
            if password == confirmation:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                return JsonResponse({"message": "Password changed"}, status=201)
            return JsonResponse({"message": "Passwords mismatch"}, status=201)
    return HttpResponseRedirect(reverse("login"))

@login_required()
@csrf_exempt
def change_password(request):
    if request.method == "POST":
        email = request.user.email
        current_password = request.POST["current_password"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        user = auth.authenticate(email=email, password=current_password)
        if user is not None:
            if password == confirmation:
                user.set_password(password)
                user.save()
                login(request, user)
    return HttpResponseRedirect(reverse("login"))

@csrf_exempt
def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "")
        password = data.get("password", "")
        confirmation = data.get("confirmation", "")

        phone = data.get("phone", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        middle_name = data.get("middle_name", "")
        birthday = data.get("birthday", "")
        disability_type = data.get("disability_type", "")

        school_id = data.get("school_id", "")
        grade_number = data.get("grade_number", "")
        grade_letter = data.get("grade_letter", "")
        school = School.objects.get(id=school_id)

        if disability_type.isdigit():
            disability_type = DisabilityType.objects.filter(id=disability_type)
            if len(disability_type) != 0:
                disability_type = disability_type[0]
        else:
            disability_type = None
        if password != confirmation:
            return JsonResponse({"message": "Password mismatch."}, status=201)
        try:
            user = User.objects.create_user(email, password)
            user.first_name = first_name
            user.middle_name  = middle_name
            user.last_name = last_name
            user.birthday = birthday
            user.phone_number = phone
            user.disability_type = disability_type

            user.role = 'ST'
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
            user.school = school
            user.school_class = school_class
            user.save()
        except IntegrityError:
            return JsonResponse({"message": "Email already taken."}, status=201)

        return JsonResponse({"message": "Account created successfully."}, status=201)
    return HttpResponseRedirect(reverse("login"))

def reg_choice(request):
    return HttpResponseRedirect(reverse("login"))

def reg_stage(request, choice, stage):
    return HttpResponseRedirect(reverse("login"))

@login_required
@csrf_exempt
def import_students_coordinator(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = students_import(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "user/import.html",{
            'form': form,
            'message': message
        })

    form = ImportDataForm()
    return render(request, "user/import.html",{
        'form': form
    })

        
@csrf_exempt
def students_report(request):
    users = User.objects.filter(role='ST')
    wb = Workbook()
    ws = wb.active
    ws.title = "Cтуденты"
    column_names = [
        "Школа","Фамилия", 
        "Имя", "Отчество", 
        "Дата регистрации", "Email", 
        "Номер телефона", "Дата регистрации",
    ]
    active_column = 1
    for name in column_names:
        ws.cell(row=1, column=active_column, value=name)
        active_column += 1
    
    active_row = 2
    for user in users:
        if len(user.bundles.all()) == 0 and len(user.school.bundles.all())!= 0:
                cell_values = {
                    "Школа": user.school.name, 
                    "Фамилия": user.last_name,
                    "Имя": user.first_name, 
                    "Отчество": user.middle_name,
                    "Email": user.email, 
                    "Номер телефона": user.phone_number,
                    "Дата регистрации": str(user.date_joined),
                }
                active_col = 1
                for key, value in cell_values.items():
                    ws.cell(row=active_row, column=active_col, value=value)
                    active_col += 1
                active_row += 1


    wb.template = False
    wb.save('students_list.xlsx')
    response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=students_list.xlsx'
    return response