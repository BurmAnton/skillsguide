import datetime
from email.policy import default
from pyexpat import model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING

from users.models import User
from schools.models import School
from education_centers.models import EducationCenter, TrainingProgram, Workshop, Competence, Criterion, FieldOfActivity, Lesson
from regions.models import Region, City

# Create your models here.
class SchoolStudentsGroup(models.Model):
    users = models.ManyToManyField(User, verbose_name="Участники группы", blank=True)
    limit = models.IntegerField("Лимит участников", default=25)

    class Meta:
        verbose_name = "Цикл профпроб"
        verbose_name_plural = "Циклы профпроб"

    def __str__(self):
        return f'Группа №{self.id}'


class TrainingCycle(models.Model):
    name = models.CharField("Назывние цикла", max_length=150)
    
    fields_of_activity = models.ManyToManyField(FieldOfActivity, verbose_name="Сферы деятельности", related_name="cycles", blank=True)
    competencies = models.ManyToManyField(Competence, verbose_name="Компетенции", related_name="cycles", blank=True)
    programs = models.ManyToManyField(TrainingProgram, verbose_name="Программы", related_name="cycles", blank=True)
    region = models.ForeignKey(Region, verbose_name="Регион", related_name="cycles", null=True, blank=True, on_delete=CASCADE)
    city = models.ForeignKey(City, verbose_name="Населённый пункт", related_name="cycles", null=True, blank=True, on_delete=CASCADE)
    schools = models.ManyToManyField(School, verbose_name="Школы участники", related_name="cycles", blank=True)
    groups = models.ManyToManyField(SchoolStudentsGroup, verbose_name="Группы", related_name="cycles", blank=False)
    start_date = models.DateField("Дата начала", null=False, blank=False)
    end_date = models.DateField("Дата окончания", null=False, blank=False)

    class Meta:
        verbose_name = "Цикл профпроб"
        verbose_name_plural = "Циклы профпроб"

    def __str__(self):
        return self.name


class TrainingStream(models.Model):
    cycle = models.ForeignKey(TrainingCycle, verbose_name="Цикл профпроб", related_name="streams", on_delete=models.CASCADE, null=True, blank=False)
    group = models.ForeignKey(SchoolStudentsGroup, verbose_name="Группы", related_name="streams", on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        verbose_name = "Учебный поток"
        verbose_name_plural = "Учебные потоки"

    def __str__(self):
        return self.name


class Training(models.Model):
    program = models.ForeignKey(TrainingProgram, verbose_name="Программа", related_name="trainings", on_delete=CASCADE)
    stream = models.ForeignKey(TrainingStream, verbose_name="Учебный поток", related_name="trainings", on_delete=CASCADE, null=True, blank=False)
    start_date = models.DateField("Дата начала", null=False, blank=False)
    end_date = models.DateField("Дата окончания", null=False, blank=False)
    group = models.ForeignKey(SchoolStudentsGroup, verbose_name="Группы", related_name="trainings", on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        verbose_name = "Расписание обучения"
        verbose_name_plural = "Расписания обучения"

    def __str__(self):
        return f'{self.program.name}({self.start_date}-{self.end_date})'


class Conference(models.Model):
    invite_link = models.URLField("Ссылка на конференцию", null=False, blank=False)
    Identifier = models.CharField("Идентификатор", max_length=150, null=False, blank=False)
    access_code = models.CharField("Код доступа", max_length=150, null=False, blank=False)
    instruction = models.CharField("Инструкция", max_length=250, null=False, blank=False)

    class Meta:
        verbose_name = "Данные для подключения"
        verbose_name_plural = "Данные для подключения"


class TrainingClass(models.Model):
    training = models.ForeignKey(Training, verbose_name="Расписание", related_name="classes", on_delete=CASCADE)
    lesson = models.ForeignKey(Lesson, verbose_name="Занятие", related_name="classes", on_delete=CASCADE)
    
    date = models.DateField("Дата проведения", null=False, blank=False)
    start_time = models.TimeField("Время начала", null=False, blank=False)
    
    is_online = models.BooleanField("Онлайн", default=False)
    workshop = models.ForeignKey(Workshop, verbose_name="Мастерская", related_name="classes", on_delete=CASCADE)
    conference = models.ForeignKey(Conference, verbose_name="Конференция", related_name="classes", on_delete=CASCADE)
    group = models.ForeignKey(SchoolStudentsGroup, verbose_name="Группы", related_name="classes", on_delete=models.CASCADE, null=True, blank=False)
    
    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"

    def __str__(self):
        return f'{self.program.name}({self.start_date}-{self.end_date})'
    

class Assessment(models.Model):
    timeslot = models.ForeignKey(Training, verbose_name="Расписание обучения", related_name="assessment", on_delete=models.CASCADE)
    grade = models.IntegerField("Оценка", null=True, blank=True)
    criterion = models.ForeignKey(Criterion, verbose_name="Критерий", related_name="assessment", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Участник", related_name="assessment", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Ассессмент"
        verbose_name_plural = "Ассессмент"


class Attendance(models.Model):
    training_class = models.ForeignKey(TrainingClass, verbose_name="Слот", related_name="attendance", on_delete=models.CASCADE)
    is_attend = models.BooleanField("Посетил", default=False)
    user = models.ForeignKey(User, verbose_name="Участник", related_name="attendance", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"
