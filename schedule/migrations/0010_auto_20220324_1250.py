# Generated by Django 3.2.8 on 2022-03-24 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0012_alter_educationcenter_trainers'),
        ('schedule', '0009_rename_program_bundle_programs'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='schedule_type',
            field=models.CharField(choices=[('ADW', 'Любые дни недели'), ('SDW', 'Конкретные дни недели')], default='SDW', max_length=3, verbose_name='Тип расписания'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='week_number',
            field=models.IntegerField(default=0, verbose_name='Номер недели'),
        ),
        migrations.AlterField(
            model_name='bundle',
            name='competencies',
            field=models.ManyToManyField(blank=True, related_name='bundles', to='education_centers.Competence', verbose_name='Компетенции'),
        ),
        migrations.AlterField(
            model_name='bundle',
            name='programs',
            field=models.ManyToManyField(blank=True, related_name='bundles', to='education_centers.TrainingProgram', verbose_name='Программы пробы'),
        ),
    ]
