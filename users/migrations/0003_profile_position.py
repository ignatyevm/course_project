# Generated by Django 2.2.1 on 2019-06-12 03:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_auto_20190524_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.CharField(
                choices=[('Студент', 'Студент'), ('Преподаватель', 'Преподаватель'), ('Ученый', 'Ученый'),
                         ('Другая', 'Другая')], default='Другая', max_length=20),
        ),
    ]