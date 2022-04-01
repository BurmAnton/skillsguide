from tabnanny import verbose
from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User, DisabilityType


class FieldOfActivity(models.Model):
    name = models.CharField("Название", max_length=70, null=False, blank=False)
    description = models.CharField("Описание", max_length=240, null=True, blank=True)

    class Meta:
        verbose_name = "Сфера деятельности"
        verbose_name_plural = "Сферы деятельности"

    def __str__(self):
        return self.name


class Competence(models.Model):
    name = models.CharField("Название компетенции", max_length=200)
    field_of_activity = models.ForeignKey(FieldOfActivity, verbose_name="Сфера деятельности", related_name="competencies", on_delete=CASCADE, null=False, blank=False)
    
    #Worldskills
    is_ws = models.BooleanField('Worldskills', default=False)
    СOMPETENCE_BLOCKS = (
        ('IT', 'Информационные и коммуникационные технологии'),
        ('SR', 'Сфера услуг'),
        ('BD', 'Строительство и строительные технологии'),
        ('MF', 'Производство и инженерные технологии'),
        ('DS', 'Творчество и дизайн'),
        ('TR', 'Транспорт и логистика'),
        ('ED', 'Образование')
    )
    block = models.CharField(max_length=2, choices=СOMPETENCE_BLOCKS, verbose_name='Блок', blank=True, null=True)
    СOMPETENCE_STAGES = (
        ('MN', 'Основная'),
        ('PR', 'Презентационная')
    )
    competence_stage = models.CharField(max_length=2, choices=СOMPETENCE_STAGES, verbose_name='Стадия', blank=True, null=True)
    СOMPETENCE_TYPES = (
        ('RU', 'WorldSkills Russia'),
        ('WSI', 'WorldSkills International'),
        ('WSE', 'WorldSkills Eurasia')
    )
    competence_type = models.CharField(max_length=3, choices=СOMPETENCE_TYPES, verbose_name='Тип', blank=True, null=True)

    class Meta:
        verbose_name = "Компетенция"
        verbose_name_plural = "Компетенции"

    def __str__(self):
        return self.name


class EducationCenter(models.Model):
    name = models.CharField("Название организации", max_length=500)
    contact_person = models.OneToOneField(User, verbose_name="Контактное лицо", related_name="education_center", on_delete=DO_NOTHING, blank=True, null=True)
    trainers = models.ManyToManyField(User, verbose_name="Преподователи", related_name="education_centers", blank=True)

    class Meta:
        verbose_name = "Центр обучения"
        verbose_name_plural = "Центры обучения"

    def __str__(self):
        return self.name


class Criterion(models.Model):
    name = models.CharField("Назывние критерия", max_length=1000)

    class Meta:
        verbose_name = "Критерий"
        verbose_name_plural = "Критерии"

    def __str__(self):
        return self.name


class TrainingProgram(models.Model):
    name = models.CharField("Название программы", max_length=300)
    description = models.CharField("Описание", max_length=1000, null=True)
    competence = models.ForeignKey(Competence, verbose_name="Компетенция", on_delete=CASCADE, related_name='programs')
    program_link =  models.CharField("Ссылка на программу", max_length=200, blank=True, null=True)
    criteria = models.ManyToManyField(Criterion, verbose_name="Критерии")

    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", related_name="programs", on_delete=CASCADE)
    attendance_limit = models.IntegerField("Максимальное кол-во участников", default=10)
    disability_types = models.ManyToManyField(DisabilityType, verbose_name="ОВЗ", blank=True)
    
    instructors = models.ManyToManyField(User, verbose_name="Преподователи", blank=True)

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        return self.name


class Workshop(models.Model):
    education_center = models.ForeignKey(EducationCenter, verbose_name="Центр обучения", on_delete=CASCADE, related_name='workshops')
    competence = models.ForeignKey(Competence, verbose_name="Компетенция",  on_delete=CASCADE, related_name='workshops')
    adress = models.CharField("Адрес", max_length=350)
    description = models.CharField("Описание", max_length=700, null=True, blank=True)

    class Meta:
        verbose_name = "Мастерская"
        verbose_name_plural = "Мастерские"

    def __str__(self):
        return f"{self.adress}"
