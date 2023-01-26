from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

from regions.models import City

class DisabilityType(models.Model):
    name = models.CharField("ОВЗ", max_length=100)
    description = models.CharField("Описание", max_length=300, blank=True, null=True)

    def __str__(self):
        return  f"{self.name}"

    class Meta:
        verbose_name = "Инвалидность"
        verbose_name_plural = "Инвалидности"


class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    birthday = models.DateField("Дата рождения", blank=True, null=True)
    ROLES = (
        ('ST', 'Студент'),
        ('SST', 'Школьник'),
        ('ADLT', 'Взрослый'),
        ('RSC', 'Представитель школы'),
        ('REC', 'Представитель ЦО'),
        ('INTS', 'Преподаватель')
    )
    role = models.CharField(max_length=4, choices=ROLES, verbose_name='Роль', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=CASCADE, null=True, related_name="residents", verbose_name="Нас. пункт проживания")
    disability_types = models.ManyToManyField(DisabilityType, verbose_name="ОВЗ", blank=True)

    is_verified = models.BooleanField("Аккаунт подтверждён", null=False, default=False)
    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.last_name == None or self.first_name == None:
            return f'{self.email}'
        if self.middle_name == None or len(self.middle_name) == 0:
            return f'{self.first_name} {self.last_name}'
        return f'{self.first_name} {self.middle_name} {self.last_name}'
        
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Parent(models.Model):
    children = models.ManyToManyField(User, verbose_name="Дети", blank=False)

    first_name = models.CharField("Имя", max_length=30, blank=False, null=False)
    last_name = models.CharField("Фамилия", max_length=30, blank=False, null=False)
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)

    def __str__(self):
        if self.last_name == None or self.first_name == None:
            return f'{self.email}'
        if self.middle_name == None:
            return f'{self.first_name[0]}. {self.last_name}'
        return f'{self.first_name[0]}.{self.middle_name[0]}. {self.last_name}'
    
    class Meta:
        verbose_name = "Родитель"
        verbose_name_plural = "Родители"

