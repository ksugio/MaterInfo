# Generated by Django 4.2 on 2024-02-27 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hardness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('prefix', models.PositiveIntegerField(default=0, verbose_name='Prefix')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('unit', models.PositiveSmallIntegerField(choices=[(0, 'HV'), (1, 'HRC'), (2, 'HB'), (3, 'HRA'), (4, 'HRB'), (5, 'HRD'), (6, 'HS'), (7, 'HRF'), (8, 'HIT')], default=0, verbose_name='Unit')),
                ('load', models.FloatField(blank=True, null=True, verbose_name='Load')),
                ('load_unit', models.PositiveSmallIntegerField(choices=[(0, 'gf'), (1, 'kgf')], default=0, verbose_name='Load Unit')),
                ('time', models.FloatField(blank=True, null=True, verbose_name='Time(s)')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sample.sample', verbose_name='Sample')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('value', models.FloatField(default=0.0, verbose_name='Value')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hardness.hardness', verbose_name='Hardness')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
