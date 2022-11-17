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


class Category(models.Model):
    category_name = models.CharField("Название", max_length=100, null=False, blank=False)
    #icon
    parent_category = models.ForeignKey(
        'self', 
        verbose_name="Родительская категория",
        null=True, 
        blank=True,
        on_delete=models.CASCADE
    )
    description = models.CharField("Краткое описание", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return  f"Склал №{self.id} ({self.address})"


class Brand(models.Model):
    pass


class Product(models.Model):
    barcode = models.CharField("Штрихкод", max_length=30, null=False, blank=False)
    product_name = models.CharField("Название", max_length=100, null=False, blank=False)
    brand = models.ForeignKey(Brand, verbose_name="Бренд", related_name="products", null=False, blank=False)
    description = models.TextField("Описание", null=True, blank=True)
    #images
    length = models.FloatField("Длина", null=True, blank=True)
    width = models.FloatField("Ширина", null=True, blank=True)
    depth = models.FloatField("Глубина", null=True, blank=True)
    weight = models.FloatField("Вес", null=True, blank=True)


    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return  f"{self.product_name} ({self.barcode})"


class TechSpec(models.Model):
    pass