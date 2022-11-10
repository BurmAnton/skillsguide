import datetime
from email.policy import default
import json
from pyexpat import model
from tabnanny import verbose
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING

from users.models import User
from schools.models import School, SchoolStudent
from education_centers.models import EducationCenter, Trainer, TrainingProgram, Workshop, Competence, Criterion, FieldOfActivity, Lesson
from regions.models import Region, City


class TrainingBundle(models.Model):
    name = models.CharField("Название набора", max_length=150)
    fields_of_activity = models.ManyToManyField(FieldOfActivity, verbose_name="Сферы деятельности", related_name="cycles", blank=True)
    competencies = models.ManyToManyField(Competence, verbose_name="Компетенции", related_name="cycles", blank=True)

    class Meta:
        verbose_name = "Набор профпроб"
        verbose_name_plural = "Наборы профпроб"

    def __str__(self):
        return self.name


class TrainingCycle(models.Model):
    name = models.CharField("Название цикла", max_length=150)
    bundle = models.ForeignKey(TrainingBundle, verbose_name="Набор профпроб", related_name="cycles", null=False, blank=False, on_delete=CASCADE)
    is_active = models.BooleanField("Текущий цикл", default=True)
    education_centers = models.ManyToManyField(EducationCenter, verbose_name="Ценрты обучения", related_name="cycles", blank=True)
    programs = models.ManyToManyField(TrainingProgram, verbose_name="Программы", related_name="cycles", blank=True)
    region = models.ForeignKey(Region, verbose_name="Регион", related_name="cycles", null=True, blank=True, on_delete=CASCADE)
    city = models.ForeignKey(City, verbose_name="Населённый пункт", related_name="cycles", null=True, blank=True, on_delete=CASCADE)
    schools = models.ManyToManyField(School, verbose_name="Школы участники", related_name="cycles", blank=True)
    students_limit = models.IntegerField("Лимит участников", null=False, blank=False)
    group_limit = models.IntegerField("Лимит для группы", null=False, blank=False)

    start_date = models.DateField("Дата начала", null=False, blank=False)
    start_time = models.TimeField("Время начала проб", null=True, blank=False)
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    is_any_day = models.BooleanField("Любой день недели", default=False)
    days_of_week = models.CharField("Дни недели", max_length=20, null=True, blank=True)
    days_per_week = models.IntegerField("Дней в неделю", null=True, blank=True)
    excluded_dates = models.CharField("Даты исключения", max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "Цикл профпроб"
        verbose_name_plural = "Циклы профпроб"

    def __str__(self):
        return self.name


class SchoolQuota(models.Model):
    training_cycle = models.ForeignKey(TrainingCycle, verbose_name="Цикл", related_name="quotas", on_delete=CASCADE)
    school = models.OneToOneField(School, verbose_name="Школа", related_name="quota", on_delete=CASCADE)
    quota = models.IntegerField("Квота школы", null=False, blank=False, default=10)

    class Meta:
        verbose_name = "Квота"
        verbose_name_plural = "Квоты"

    def __str__(self):
        return f'{self.school} ({self.training_cycle}) - {self.quota}'


class TrainingStream(models.Model):
    cycle = models.ForeignKey(TrainingCycle, verbose_name="Цикл профпроб", related_name="streams", on_delete=models.CASCADE, null=True, blank=False)
    students_limit = models.IntegerField("Лимит участников", default=25)
    students = models.ManyToManyField(SchoolStudent, verbose_name="Участники потока", related_name="streams", blank=True)


    class Meta:
        verbose_name = "Учебный поток"
        verbose_name_plural = "Учебные потоки"

    def __str__(self):
        return f'{self.cycle} (id - {self.id})'


class AvailableDate(models.Model):
    stream = models.ForeignKey(TrainingStream, verbose_name="Поток", related_name="available_dates", on_delete=models.CASCADE, null=True, blank=False)
    date = models.DateField("Доступная дата", null=False, blank=False)
    week_number = models.IntegerField("Номер недели", null=True, blank=True)
    busy = models.BooleanField("Занят", default=False)
    is_unavailable = models.BooleanField("Недоступно", default=False)

    class Meta:
        verbose_name = "Доступная дата"
        verbose_name_plural = "Доступные даты"

    def __str__(self):
        return f'{self.date} ({self.stream})'


class Training(models.Model):
    program = models.ForeignKey(TrainingProgram, verbose_name="Программа", related_name="trainings", on_delete=CASCADE)
    stream = models.ForeignKey(TrainingStream, verbose_name="Учебный поток", related_name="trainings", on_delete=CASCADE, null=True, blank=False)
    start_date = models.DateField("Дата начала", null=False, blank=False)
    end_date = models.DateField("Дата окончания", null=False, blank=False)
    stream = models.ForeignKey(TrainingStream, verbose_name="Поток", related_name="trainings", on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        verbose_name = "Расписание обучения"
        verbose_name_plural = "Расписания обучения"

    def __str__(self):
        return f'{self.program.name}({self.start_date}-{self.end_date})'


class Conference(models.Model):
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="conferences", on_delete=CASCADE)
    name = models.CharField("Название", max_length=70)
    invite_link = models.URLField("Ссылка на конференцию", null=False, blank=False)
    Identifier = models.CharField("Идентификатор", max_length=150, null=False, blank=False)
    access_code = models.CharField("Код доступа", max_length=150, null=False, blank=False)
    instruction = models.CharField("Инструкция", max_length=250, null=False, blank=False)

    class Meta:
        verbose_name = "Данные для подключения"
        verbose_name_plural = "Данные для подключения"


class ProfTest(models.Model):
    ed_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="tests", on_delete=CASCADE)
    program = models.ForeignKey(TrainingProgram, verbose_name="Программа", related_name="tests", on_delete=CASCADE)
    stream = models.ForeignKey(TrainingStream, verbose_name="Учебный поток", related_name="tests", on_delete=CASCADE, null=True, blank=False)
    date = models.DateField("Дата проведения", null=True, blank=True)
    start_time = models.TimeField("Время начала", null=True, blank=True)
    
    trainer = models.ForeignKey(Trainer, verbose_name="Преподователь", related_name="tests", on_delete=models.CASCADE, null=True, blank=True)
    is_online = models.BooleanField("Онлайн", default=False)
    workshop = models.ForeignKey(Workshop, verbose_name="Мастерская", related_name="tests", on_delete=CASCADE, null=True)
    conference = models.ForeignKey(Conference, verbose_name="Конференция", related_name="tests", on_delete=CASCADE, null=True)

    class Meta:
        verbose_name = "Профпроба"
        verbose_name_plural = "Профпробы"

    def __str__(self):
        return f'{self.program.name}({self.start_time} {self.date})'


class TrainingClass(models.Model):
    training = models.ForeignKey(Training, verbose_name="Расписание", related_name="classes", on_delete=CASCADE)
    lesson = models.ForeignKey(Lesson, verbose_name="Занятие", related_name="classes", on_delete=CASCADE)
    
    date = models.DateField("Дата проведения", null=False, blank=False)
    start_time = models.TimeField("Время начала", null=False, blank=False)
    
    is_online = models.BooleanField("Онлайн", default=False)
    workshop = models.ForeignKey(Workshop, verbose_name="Мастерская", related_name="classes", on_delete=CASCADE)
    conference = models.ForeignKey(Conference, verbose_name="Конференция", related_name="classes", on_delete=CASCADE)
    stream = models.ForeignKey(TrainingStream, verbose_name="Поток", related_name="classes", on_delete=models.CASCADE, null=True, blank=False)
    
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
