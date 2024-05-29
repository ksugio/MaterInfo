# Generated by Django 4.2 on 2024-05-28 04:01

from django.db import migrations, models
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ('collect', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collect',
            name='unique',
            field=models.CharField(default=project.models.UniqueStr, max_length=36, verbose_name='Unique String'),
        ),
        migrations.AddField(
            model_name='filter',
            name='unique',
            field=models.CharField(default=project.models.UniqueStr, max_length=36, verbose_name='Unique String'),
        ),
    ]