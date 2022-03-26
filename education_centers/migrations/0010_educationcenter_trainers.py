# Generated by Django 3.2.8 on 2022-03-22 03:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('education_centers', '0009_alter_trainingprogram_instructors'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenter',
            name='trainers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Преподователи'),
        ),
    ]
