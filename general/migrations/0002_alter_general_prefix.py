# Generated by Django 4.2 on 2024-05-21 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='general',
            name='prefix',
            field=models.CharField(blank=True, max_length=36, verbose_name='Prefix'),
        ),
    ]