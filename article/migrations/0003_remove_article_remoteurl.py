# Generated by Django 4.2 on 2025-03-07 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_file_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='remoteurl',
        ),
    ]
