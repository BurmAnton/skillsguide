import datetime
from pyexpat import model
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING

from users.models import User, School
from education_centers.models import EducationCenter, TrainingProgram, Workshop, Competence, Criterion

# Create your models here.
class Bundle(models.Model):
    name = models.CharField("Название набора", max_length=100, default="")
    competencies = models.ManyToManyField(Competence, verbose_name="Компетенции", related_name="bundles", blank=True)
    programs = models.ManyToManyField(TrainingProgram, verbose_name="Программы пробы", related_name="bundles", blank=True)
    edu_centers = models.ManyToManyField(EducationCenter, verbose_name="Центры обучения", related_name="train_cycles", blank=True)
    schools = models.ManyToManyField(School, verbose_name="Школы", related_name="bundles")
    participants = models.ManyToManyField(User, verbose_name="Участники", related_name='bundles', blank=True)
    
    class Meta:
        verbose_name = "Набор проб"
        verbose_name_plural = "Наборы проб"


    def __str__(self):
        return  f"{self.name}"


class Stream(models.Model):
    bundle = models.ForeignKey(Bundle, verbose_name="Набор проб", related_name="streams", on_delete=CASCADE, null=True)
    start_date = models.DateField("Дата начала", null=True)
    attendance_limit = models.IntegerField("Максимальное кол-во участников", default=10)
    participants = models.ManyToManyField(User, verbose_name="Участники", related_name='streams', blank=True)
    SCHEDULE_TYPE= (
        ('ADW', 'Любые дни недели'),
        ('SDW', 'Конкретные дни недели')
    )
    schedule_type = models.CharField("Тип расписания", choices=SCHEDULE_TYPE, default='SDW', max_length=3)
    week_limit = models.IntegerField("Колво занятий в неделю", default=2)

    class Meta:
        verbose_name = "Поток"
        verbose_name_plural = "Потоки"
    
    def __str__(self):
        return f'Поток №{self.id} (Набор "{self.bundle}")'


class TimeSlot(models.Model):
    stream = models.ForeignKey(Stream, verbose_name="Поток", related_name="slots", on_delete=CASCADE, null=True)
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", related_name="slots", blank=True, null=True, on_delete=CASCADE)
    program = models.ForeignKey(TrainingProgram, verbose_name="Программа", related_name="slots", blank=True, null=True, on_delete=CASCADE)
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="slots", blank=True, null=True, on_delete=CASCADE)

    date = models.DateField("Дата", null=True)
    time = models.TimeField("Время начала", auto_now=False, auto_now_add=False, null=True)
    week_number = models.IntegerField("Номер недели", default=0)
    
    online = models.BooleanField("Онлайн", default=False)
    workshop = models.ForeignKey(Workshop, verbose_name="Мастерская", related_name="slots", blank=True, null=True, on_delete=DO_NOTHING)

    participants = models.ManyToManyField(User, verbose_name="Участники", related_name='time_slots', blank=True)
    trainer = models.ForeignKey(User, verbose_name="Преподователь", related_name="slots", on_delete=CASCADE, null=True)
    
    zoom_link = models.URLField("Ссылка на конференцию", max_length=400, blank=True, null=True)
    zoom_instruction = models.TextField("Инструкция по подключению", default="", blank=True, null=True)

    SCHEDULE_TYPE= (
        ('FTR', 'Будущая'),
        ('CRNT', 'Текущая'),
        ('ASSM', 'Требует оценки'),
        ('END', 'Завершёна'),
    )
    status = models.CharField("Тип расписания", choices=SCHEDULE_TYPE, default='FTR', max_length=4)
    
    is_nonprofit = models.BooleanField("На безвозмездной основе", default=True)

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    def __str__(self):
        return  f"{self.id} {self.competence} – {self.date} {self.time}"


class Assessment(models.Model):
    timeslot = models.ForeignKey(TimeSlot, verbose_name="Слот", related_name="assessment", on_delete=models.CASCADE)
    grade = models.IntegerField("Оценка", validators=[MinValueValidator(1),MaxValueValidator(5)], null=True, blank=True)
    criterion = models.ForeignKey(Criterion, verbose_name="Критерий", related_name="assessment", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Ученик", related_name="assessment", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Ассессмент"
        verbose_name_plural = "Ассессмент"


class Attendance(models.Model):
    timeslot = models.ForeignKey(TimeSlot, verbose_name="Слот", related_name="attendance", on_delete=models.CASCADE)
    is_attend = models.BooleanField("Посетил", default=False)
    user = models.ForeignKey(User, verbose_name="Ученик", related_name="attendance", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"
