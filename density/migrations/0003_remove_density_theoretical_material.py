# Generated by Django 4.2 on 2025-03-07 23:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('density', '0002_alter_density_prefix'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='density',
            name='theoretical',
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('density', models.FloatField(verbose_name='Density')),
                ('fraction', models.FloatField(blank=True, null=True, verbose_name='Fraction')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='density.density', verbose_name='Material')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
