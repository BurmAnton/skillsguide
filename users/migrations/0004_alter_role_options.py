# Generated by Django 4.1.3 on 2022-11-14 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_group_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Роль', 'verbose_name_plural': 'Роли'},
        ),
    ]
