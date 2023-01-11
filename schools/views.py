from datetime import datetime, timedelta
import secrets
import string

from email import message
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from schedule.models import Assessment, Attendance, ProfTest, TrainingCycle, TrainingStream

from users.models import User
from regions.models import City, TerAdministration, Address
from .models import Grade, School, SchoolContactPersone, SchoolStudent

from education_centers.forms import ImportDataForm
from users.mailing import send_mail
from . import imports

#ЛК школы
@csrf_exempt
def school_profile(request, school_id):
    school = get_object_or_404(School, id=school_id)
    message = ""
    if request.method == "POST":
        if 'exclude-student' in request.POST:
            student_id = request.POST[f'student_id']
            student = SchoolStudent.objects.get(id=student_id)
            test_id = request.POST[f'test_id']
            test = ProfTest.objects.get(id=test_id)
            test.students.remove(student)
            test.save()
        else:
            message = "Success"
            for student in school.students.all():
                stream = request.POST[f'student{student.id}_stream']
                if stream == "None":
                    student.streams.clear()
                elif stream != "Selected":
                    stream = get_object_or_404(TrainingStream, id=stream)
                    if len(stream.students.all()) < stream.students_limit:
                        student.streams.clear()
                        student.tests.clear()
                        Assessment.objects.filter(student=student).delete()
                        Attendance.objects.filter(student=student).delete()
                        student.streams.add(stream)
                    else:
                        message = "StreamOverFlow"
                student.save()
                if stream != "None" and stream != "Selected":
                    for test in stream.tests.all():
                        test.students.add(*stream.students.all())
                        test.save()
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
    contact = get_object_or_404(SchoolContactPersone, school=school.id)
    
    students = school.students.all()
    students_count = len(students)
    streams = TrainingStream.objects.filter(students__in=students)
    two_weeks = datetime.today() + timedelta(14)
    tests = ProfTest.objects.filter(stream__in=streams, date__gte=datetime.today(), date__lte=two_weeks).order_by('date', 'start_time')

    return render(request, "schools/school_profile.html",{
        "cities": City.objects.all(),
        "school": school,
        "students_count": students_count,
        'tests': tests,
        'contact': contact,
        "message": message
    })

@login_required
def grades_list(request, school_id):
    school = get_object_or_404(School, id=school_id)
    contact = get_object_or_404(SchoolContactPersone, school=school.id)

    grades = Grade.objects.filter(school=school)

    return render(request, "schools/grades_list.html",{
        "school": school,
        'contact': contact,
        "grades": grades,
    })

@login_required
def grade(request, school_id, grade_id):
    school = get_object_or_404(School, id=school_id)
    contact = get_object_or_404(SchoolContactPersone, school=school.id)
    
    grade = get_object_or_404(Grade, id=grade_id)
    
    return render(request, "schools/grade.html",{
        "school": school,
        'contact': contact,
        "grade": grade,
    })

@login_required
def school_tests_list(request, school_id):
    school = get_object_or_404(School, id=school_id)
    contact = get_object_or_404(SchoolContactPersone, school=school.id)

    students = school.students.all()
    tests = ProfTest.objects.filter(students__in=students).exclude(date=None).order_by('-date', '-start_time')

    return render(request, "schools/tests_list.html",{
        "school": school,
        'contact': contact,
        "tests": tests,
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
        duplicates = School.objects.filter(inn=inn)
        if len(duplicates) != 0:
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
