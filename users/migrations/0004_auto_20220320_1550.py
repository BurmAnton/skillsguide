# Generated by Django 3.2.8 on 2022-03-20 11:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='school_coordinator',
        ),
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AddField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='users.school', verbose_name='Школа'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('ST', 'Школьник'), ('CO', 'Представитель ЦО'), ('TCH', 'Преподователь'), ('COR', 'Координатор')], max_length=3, null=True, verbose_name='Роль'),
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_number', models.IntegerField(validators=[django.core.validators.MaxValueValidator(11), django.core.validators.MinValueValidator(1)], verbose_name='Номер класса')),
                ('grade_letter', models.CharField(max_length=4, verbose_name='Буква класса')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='users.school', verbose_name='Школа')),
            ],
            options={
                'verbose_name': 'Класс',
                'verbose_name_plural': 'Классы',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='school_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='users.schoolclass', verbose_name='Школный класс'),
        ),
    ]
