from django.db.models.deletion import CASCADE
from django.db import models

# Create your models here.
class Country(models.Model):
    name = models.CharField("Название страны", max_length=100, blank=False, null=False)
    
    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class City(models.Model):
    name = models.CharField("Название", max_length=100, blank=False, null=False)
    region = models.ForeignKey(Country, on_delete=CASCADE, related_name="cities", verbose_name="Страна")

    def __str__(self):
        return  f"{self.name}"

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"


class Address(models.Model):
    city = models.ForeignKey(
        City, 
        on_delete=CASCADE, 
        related_name="addresses", 
        verbose_name="Населённый пункт"
    )
    street = models.CharField("Улица", max_length=200, blank=False, null=False)
    building_number = models.CharField("Дом", max_length=10, blank=False, null=False)
    building = models.CharField("Корпус", max_length=10, blank=True, null=True)
    postcode = models.CharField("Почтовый индекс", max_length=20, blank=True, null=True)

    def __str__(self):
        address = f'{self.city}, ул. {self.street}, дом {self.building_number}'
        if self.building is not None:
            address += f', корп. {self.building}'
        if self.postcode is not None:
            address += (f' ({self.postcode})')
        return address
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
