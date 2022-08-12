from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.core.validators import MaxValueValidator, MinValueValidator

from regions.models import City, TerAdministration
from users.models import User

# Create your models here.
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


class Grade(models.Model):
    school = models.ForeignKey(School, verbose_name="Школа", related_name="classes", on_delete=CASCADE)
    grade = models.IntegerField("Номер класса", validators=[MaxValueValidator(12),MinValueValidator(1)])
    grade_letter = models.CharField("Буква класса", max_length=4)
    is_graduated = models.BooleanField("Выпустился", default=False)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return  f"{self.grade_number}{self.grade_letter} – {self.school}"


class SchoolStudent(models.Model):
    user = models.OneToOneField(User, related_name="school_student", verbose_name="Пользователь", on_delete=CASCADE)
    school = models.ForeignKey(School, related_name="students", verbose_name="Школа", on_delete=CASCADE)
    grade = models.ForeignKey(Grade, related_name="students", verbose_name="Класс", on_delete=CASCADE)
    is_graduated = models.BooleanField("Закончил школу", default=False)

    def __str__(self):
        return f'{self.user} ({self.school.name})'

    class Meta:
        verbose_name = "Школьник"
        verbose_name_plural = "Школьники"


class SchoolContactPersone(models.Model):
    user = models.OneToOneField(User, verbose_name="Контактное лицо", related_name="school_contact", on_delete=DO_NOTHING)
    school = models.OneToOneField(School, verbose_name="Школа", related_name="school_contact", on_delete=DO_NOTHING)

    def __str__(self):
        return f'{self.user} ({self.school.name})'

    class Meta:
        verbose_name = "Представитель школы"
        verbose_name_plural = "Представители школ"

