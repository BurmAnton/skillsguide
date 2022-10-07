from tabnanny import verbose
from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User, DisabilityType
from regions.models import City, Address


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


class EducationCenterType(models.Model):
    type_name = models.CharField("Тип учебного заведения", max_length=200, blank=False, null=False)
    
    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = "Тип учебного завдения"
        verbose_name_plural = "Типология учебных заведений"


class EducationCenter(models.Model):
    inn = models.CharField("ИНН", max_length=20, blank=True, null=True)
    name = models.CharField("Название организации", max_length=500, blank=False, null=False)
    short_name = models.CharField("Краткое название", max_length=50, blank=False, null=True)
    
    address = models.ForeignKey(Address, on_delete=DO_NOTHING, verbose_name="Адрес", related_name="education_centers", null=True)

    is_trains = models.BooleanField("Проводит обучение", default=False)
    trainers = models.ManyToManyField(User, verbose_name="Преподователи", related_name="education_centers", blank=True)

    contact_person = models.OneToOneField(
        User, 
        verbose_name="Контактное лицо", 
        related_name="education_center", 
        on_delete=DO_NOTHING, 
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name = "Центр обучения"
        verbose_name_plural = "Центры обучения"


class Faculty(models.Model):
    faculty_name = models.CharField("Название факультета", max_length=200, blank=False, null=False)
    edu_center = models.ForeignKey(EducationCenter, verbose_name="Учебное заведение", related_name="faculties", on_delete=CASCADE)

    def __str__(self):
        return f'{self.faculty_name} ({self.edu_center.short_name})'

    class Meta:
        verbose_name = "Центр обучения"
        verbose_name_plural = "Центры обучения"


class Speciality(models.Model):
    name = models.CharField("Название специальности", max_length=200, blank=False, null=False)
    speciality_code = models.CharField("Код специалности", max_length=15, blank=False, null=False)
    faculties = models.ManyToManyField(
        Faculty, 
        verbose_name="Факультет", 
        related_name="specialities", 
        blank=True
    )

    def __str__(self):
        return f'{self.name} ({self.code})'
    
    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"


class Student(models.Model):
    user = models.OneToOneField(User, related_name="student", verbose_name="Пользователь", on_delete=CASCADE)
    edu_center = models.ForeignKey(
        EducationCenter, 
        related_name="students", 
        verbose_name="Образовательное учреждение", 
        on_delete=CASCADE
    )
    speciality = models.ForeignKey(
        Speciality, 
        related_name="Специальность", 
        verbose_name="students",
        on_delete=DO_NOTHING,
        null=True
    )
    year = models.IntegerField("Год обучения", null=False, blank=False)
    DEGREE_TYPES = (
        ('UG', 'Бакалавриат'),
        ('MGT', 'Магистратура'),
        ('SPC', 'Специалитет'),
        ('HQP', 'Подготовка кадров высшей квалификации'),
    )
    degree_type = models.CharField(
        "Вид образования", 
        choices=DEGREE_TYPES, 
        max_length=3, 
        blank=False, 
        null=False
    )
    is_graduated = models.BooleanField("Выпустился", default=False)

    def __str__(self):
        return f'{self.user} ({self.speciality.name})'

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"


class Criterion(models.Model):
    name = models.CharField("Назывние критерия", max_length=1000)
    СOMPETENCE_TYPES = (
        ('SFT', 'SoftSkill'),
        ('HRD', 'HardSkill'),
    )
    skill_type = models.CharField(max_length=3, choices=СOMPETENCE_TYPES, verbose_name='Тип', default='HRD')

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
    criteria = models.ManyToManyField(Criterion, verbose_name="Критерии", related_name="programs")

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
    adress = models.ForeignKey(Address, on_delete=DO_NOTHING, verbose_name="Адрес", related_name="workshops", null=True)
    description = models.CharField("Описание", max_length=700, null=True, blank=True)

    class Meta:
        verbose_name = "Мастерская"
        verbose_name_plural = "Мастерские"

    def __str__(self):
        return f"{self.adress}"
