from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class Role(models.Model):
    role_name = models.CharField("Название", max_length=30, blank=True, null=True)
    
    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class User(AbstractUser):
    username = None
    middle_name = models.CharField("Отчество", max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
    role = models.ForeignKey(Role, verbose_name="Роль", related_name="users", on_delete=CASCADE, blank=False, null=True)

    is_verified = models.BooleanField("Аккаунт подтверждён", null=False, default=False)
    code = models.CharField("Код подтверждения", max_length=10, blank=True, null=True, default=None)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.last_name == None or self.first_name == None:
            return f'{self.email}'
        if self.middle_name == None:
            return f'{self.last_name} {self.first_name}'
        return f'{self.last_name} {self.first_name} {self.middle_name}'
        
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Group(Group):
    class Meta:
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"


class Permission(Permission):
    class Meta:
        verbose_name = "Разрешения"
        verbose_name_plural = "Разрешения"

