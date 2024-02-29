from django.db import models
from django.urls import reverse
from django.utils import timezone, crypto
from django.utils.module_loading import import_string
from accounts.models import CustomUser
from config.settings import RANDOM_STRING_LENGTH, FILE_ITEMS
import requests
import os
import uuid

def UploadTo(instance, filename):
    split = os.path.splitext(os.path.basename(filename))
    randomstr = crypto.get_random_string(length=RANDOM_STRING_LENGTH)
    newname = '%s_%s%s' % (split[0], randomstr, split[1])
    if hasattr(instance, 'created_by'):
        return '%s/%s' % (instance.created_by.username, newname)
    elif hasattr(instance, 'updated_by'):
        return '%s/%s' % (instance.updated_by.username, newname)

def ModelUploadTo(instance, filename):
    split = os.path.splitext(os.path.basename(filename))
    randomstr = crypto.get_random_string(length=RANDOM_STRING_LENGTH)
    newname = '%s_%s%s' % (instance.__class__.__name__, randomstr, split[1])
    if hasattr(instance, 'created_by'):
        return '%s/%s' % (instance.created_by.username, newname)
    elif hasattr(instance, 'updated_by'):
        return '%s/%s' % (instance.updated_by.username, newname)

def UpperModelUploadTo(instance, filename):
    split = os.path.splitext(os.path.basename(filename))
    randomstr = crypto.get_random_string(length=RANDOM_STRING_LENGTH)
    newname = '%s%s_%s%s' % (instance.upper.__class__.__name__, instance.__class__.__name__, randomstr, split[1])
    if hasattr(instance, 'created_by'):
        return '%s/%s' % (instance.created_by.username, newname)
    elif hasattr(instance, 'updated_by'):
        return '%s/%s' % (instance.updated_by.username, newname)

def UniqueID():
    return str(uuid.uuid4())

class Created(models.Model):
    upper = None
    created_by = models.ForeignKey(CustomUser, verbose_name='Created by', on_delete=models.PROTECT,
                                   related_name="%(app_label)s_%(class)s_created_by")
    created_at = models.DateTimeField(verbose_name='Created at', default=timezone.now)

    class Meta:
        abstract = True

class Updated(models.Model):
    upper = None
    updated_by = models.ForeignKey(CustomUser, verbose_name='Updated by', on_delete=models.PROTECT,
                                   related_name="%(app_label)s_%(class)s_updated_by")
    updated_at = models.DateTimeField(verbose_name='Updated at')

    def save(self, *args, **kwargs):
        auto_now = kwargs.pop('updated_at_auto_now', True)
        if auto_now:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class Remote(models.Model):
    remoteid = models.IntegerField(verbose_name='Remote ID', blank=True, null=True)
    remoteat = models.DateTimeField(verbose_name='Remote updated at', blank=True, null=True)
    localupd = models.BooleanField(verbose_name='Local updated', default=False)

    def save(self, *args, **kwargs):
        self.localupd = kwargs.pop('localupd', True)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class RemoteRoot(Remote):
    remoteurl = models.URLField(verbose_name='Remote URL', max_length=200, blank=True)

    class Meta:
        abstract = True

class Client(models.Model):
    server = models.PositiveSmallIntegerField(verbose_name='Server', default=0)
    job_id = models.PositiveIntegerField(verbose_name='JOb ID', blank=True, null=True)
    job_uuid = models.CharField(verbose_name='Job UUID', max_length=40, default='00000000')
    job_status = models.CharField(verbose_name='Job Status', max_length=16, default='not submitted')
    job_order = models.PositiveSmallIntegerField(verbose_name='Job Order', default=0)

    class Meta:
        abstract = True

class Project(Created, Updated, RemoteRoot):
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Active'), (1, 'Stop'), (2, 'Finish'), (3, 'Published'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    member = models.ManyToManyField(CustomUser, verbose_name='Member', related_name='project_member')

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('project:list')

    def get_detail_url(self):
        return reverse('project:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('project:update', kwargs={'pk': self.id})

def CreateUserProject(user):
    proj = Project.objects.create(created_by=user, updated_by=user, title=user.username + 'Project')
    proj.member.add(user)
    proj.save()
    return proj

# @receiver(post_save, sender=CustomUser)
# def create_project(sender, **kwargs):
#     if kwargs['created']:
#         user = kwargs['instance']
#         proj = Project.objects.create(created_by=user, updated_by=user, title=user.username + 'Project')
#         proj.member.add(user)
#         proj.save()

class Prefix(Created, Updated, Remote):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    prefix = models.CharField(verbose_name='Prefix', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.prefix

    def get_list_url(self):
        return reverse('project:prefix_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('project:prefix_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('project:prefix_update', kwargs={'pk': self.id})

class PrefixPtr(models.Model):
    prefix = models.PositiveIntegerField(verbose_name='Prefix', default=0)
    default_prefix = ''

    def prefix_display(self):
        try:
            return Prefix.objects.get(id=self.prefix).prefix
        except:
            if self.default_prefix:
                return self.default_prefix
            else:
                return self.__class__.__name__

    def prefix_add(self, params, imkey=''):
        nparams = {}
        if imkey:
            for key, value in params.items():
                nkey = self.prefix_display() + '_' + imkey + '_' + key
                nparams[nkey] = value
        else:
            for key, value in params.items():
                nkey = self.prefix_display() + '_' + key
                nparams[nkey] = value
        return nparams

    class Meta:
        abstract = True

class FileSearch:
    def file_search(self, url):
        for dic in FILE_ITEMS:
            lurl = url.split('/')
            path = reverse(dic['FileName'], args=range(1))
            lpath = path.split('/')
            if lurl[:-2] == lpath[:-2] and lurl[-1] == lpath[-1]:
                cls = import_string(dic['Model'])
                model = cls.objects.filter(pk=lurl[-2])
                if model:
                    return getattr(model[0], dic['FileField'])
        return None
