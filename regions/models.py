from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.
class Region(models.Model):
    name = models.CharField("Название субъекта", max_length=100, blank=False, null=False)
    
    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "Субъект РФ"
        verbose_name_plural = "Субъекты РФ"


class CityType(models.Model):
    name = models.CharField("Название", max_length=100, blank=False, null=False)
    short_name = models.CharField("Название", max_length=15, blank=False, null=False)

    def __str__(self):
        return  self.short_name

    class Meta:
        verbose_name = "Тип населённого пункта"
        verbose_name_plural = "Типы населённых пунктов"


class City(models.Model):
    name = models.CharField("Название", max_length=100, blank=False, null=False)
    city_type = models.ForeignKey(CityType, on_delete=CASCADE, related_name="cities", verbose_name="Тип населённого пункта") 
    region = models.ForeignKey(Region, on_delete=CASCADE, related_name="cities", verbose_name="Субъект Российской Федерации")

    def __str__(self):
        return  f"{self.city_type} {self.name}"

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"


class TerAdministration(models.Model):
    name = models.CharField("Тер. управление", max_length=100, blank=False, null=False)
    region = models.ForeignKey(Region, on_delete=CASCADE, related_name="ter_administrations", verbose_name="Субъект Российской Федерации")
    
    def __str__(self):
        return  self.name
        
    class Meta:
        verbose_name = "Тер. управление"
        verbose_name_plural = "Тер. управления"



class Address(models.Model):
    city = models.ForeignKey(
        City, 
        on_delete=CASCADE, 
        related_name="addresses", 
        verbose_name="Населённый пункт"
    )
    street = models.CharField("Улица", max_length=200, blank=False, null=False)
    building_number = models.CharField("Дом", max_length=10, blank=False, null=False)
    floor = models.IntegerField("Этаж", blank=True, null=True)
    apartment = models.CharField("Аудитория", max_length=10, blank=True, null=True)

    def __str__(self):
        if self.floor is not None and self.apartment is not None:
            return f'{self.city}, ул. {self.street}, дом №{self.building_number}, {self.floor} этаж, каб. {self.apartment}'
        if self.apartment is not None:
            return f'{self.city}, ул. {self.street}, дом {self.building_number}, каб. {self.apartment}'
        return f'{self.city}, ул. {self.street}, дом {self.building_number}'
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"