from django.db import models
from django.db.models.deletion import DO_NOTHING, CASCADE

from users.models import User
from regions.models import Address

# Create your models here.
class Partner(models.Model):
    pass


class Warehouse(models.Model):
    address = models.ForeignKey(
        Address, 
        verbose_name="Адрес", 
        related_name="warehouses", 
        on_delete=CASCADE,
        null=False,
        blank=False
    )
    storekeeper = models.ForeignKey(
        User, 
        verbose_name="Кладовщик", 
        related_name="warehouses",
        on_delete=DO_NOTHING,
        null=True,
        blank=True
    )
    #Партнерский склад
    is_external = models.BooleanField("Партнёрский склад", default=False)
    partner = models.ForeignKey(
        Partner,
        verbose_name="Партнёр", 
        related_name="warehouses",
        on_delete=DO_NOTHING,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return  f"Склал №{self.id} ({self.address})"