# Generated by Django 4.2 on 2024-02-27 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import project.models
import public.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('article', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Public',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('path', models.CharField(max_length=32, verbose_name='Path')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('header_color', models.CharField(default='#F5F5F5', max_length=32, verbose_name='Header Color')),
                ('header_image', models.ImageField(blank=True, upload_to=public.models.HeaderImageUploadTo, verbose_name='Header Image')),
                ('style_css', models.TextField(blank=True, verbose_name='Style CSS')),
                ('file', models.FileField(blank=True, null=True, upload_to=public.models.PublicUploadTo, verbose_name='HTML File')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('url', models.URLField(verbose_name='URL')),
                ('order', models.SmallIntegerField(verbose_name='Order')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public.public', verbose_name='Public')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('url', models.CharField(max_length=100, verbose_name='URL')),
                ('key', models.CharField(max_length=100, verbose_name='Key')),
                ('filename', models.CharField(blank=True, max_length=100, verbose_name='Filename')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public.public', verbose_name='Public')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, project.models.FileSearch),
        ),
        migrations.CreateModel(
            name='PublicArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Posted at')),
                ('file', models.FileField(blank=True, null=True, upload_to=public.models.PublicUploadTo, verbose_name='HTML File')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='article.article', verbose_name='Article')),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Posted by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public.public', verbose_name='Public')),
            ],
            bases=(models.Model, project.models.FileSearch),
        ),
    ]