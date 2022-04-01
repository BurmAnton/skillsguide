from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import CustomUserManager


class DisabilityType(models.Model):
    name = models.CharField("ОВЗ", max_length=100)
    description = models.CharField("Описание", max_length=300, blank=True, null=True)

    class Meta:
        verbose_name = "Инвалидность"
        verbose_name_plural = "Инвалидности"

    def __str__(self):
        return  f"{self.name}"


class Group(Group):
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Permission(Permission):
    pass


class TerAdministration(models.Model):
    name = models.CharField("Тер. управление", max_length=100, blank=False, null=False)
    
    def __str__(self):
        return  self.name
        
    class Meta:
        verbose_name = "Тер. управление"
        verbose_name_plural = "Тер. управления"


class City(models.Model):
    name = models.CharField("Название", max_length=100, blank=False, null=False)
    
    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"


class School(models.Model):
    inn = models.CharField("ИНН", max_length=20, blank=True, null=True)
    name = models.CharField("Название школы", max_length=100)
    specialty = models.CharField("Уклон школы", max_length=50, blank=True, null=True)

    ter_administration = models.ForeignKey(TerAdministration, verbose_name="Тер. управление", related_name="adm_schools", on_delete=DO_NOTHING, null=True, blank=True)
    city = models.ForeignKey(City, verbose_name="Город", related_name="cities_schools", on_delete=DO_NOTHING, null=True, blank=True)
    adress = models.CharField("Адрес", max_length=250, blank=True, null=True)


    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self):
        return  f"{self.name}({self.city})"


class SchoolClass(models.Model):
    school = models.ForeignKey(School, verbose_name="Школа", related_name="classes", on_delete=CASCADE)
    grade_number = models.IntegerField("Номер класса", validators=[MaxValueValidator(11),MinValueValidator(1)])
    grade_letter = models.CharField("Буква класса", max_length=4)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return  f"{self.grade_number}{self.grade_letter} – {self.school}"


class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    birthday = models.DateField("Дата рождения", blank=True, null=True)
    ROLES = (
        ('ST', 'Школьник'),
        ('SCH', 'Представитель школы'),
        ('CO', 'Представитель ЦО'),
        ('TCH', 'Преподователь'),
        ('COR', 'Координатор')
    )
    role = models.CharField(max_length=3, choices=ROLES, verbose_name='Роль', blank=True, null=True)
    school = models.ForeignKey(School, verbose_name="Школа", related_name="students", blank=True, null=True, on_delete=DO_NOTHING)
    school_class = models.ForeignKey(SchoolClass, verbose_name="Школный класс", related_name="students", blank=True, null=True, on_delete=DO_NOTHING)
    disability_types = models.ManyToManyField(DisabilityType, verbose_name="ОВЗ", blank=True)

    REL_STATUS = (
        ('NOT', 'Неперенесённый'),
        ('NLOG', 'Неавторизовался'),
        ('LOG', 'Авторизовался')
    )
    relocate_status = models.CharField(max_length=4, choices=REL_STATUS, verbose_name='Статус переноса', default="NOT")

    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name is not None and self.middle_name is not None and self.last_name is not None:
            return f'{self.last_name} {self.first_name[0]}.{self.middle_name[0]}.'
        return f'{self.email}'
            
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class SchoolContactPersone(models.Model):
    user = models.OneToOneField(User, verbose_name="Контактное лицо", related_name="school_contact", on_delete=DO_NOTHING)
    school = models.OneToOneField(School, verbose_name="Школа", related_name="school_contact", on_delete=DO_NOTHING)

    def __str__(self):
        return f'{self.user} ({self.school.name})'

    class Meta:
        verbose_name = "Представитель школы"
        verbose_name_plural = "Представители школ"