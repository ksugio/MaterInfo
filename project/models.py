from django.db import models
from django.urls import reverse
from django.utils import timezone, crypto
from django_celery_results.models import TaskResult
from accounts.models import CustomUser
from config.settings import RANDOM_STRING_LENGTH
import os

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
    pass

def UniqueStr():
    return crypto.get_random_string(length=RANDOM_STRING_LENGTH)

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
    remoteauth = models.CharField(verbose_name='Remote auth', max_length=10, blank=True)
    remotelink = models.URLField(verbose_name='Remote link', max_length=200, blank=True)
    remotelog = models.TextField(verbose_name='Remote log', blank=True)

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

class Task(models.Model):
    task_id = models.CharField(verbose_name='Task ID', max_length=40, blank=True)

    class Meta:
        abstract = True

# class RemoteTask(Task):
#     remotelog = models.TextField(verbose_name='Log', blank=True)
#
#     class Meta:
#         abstract = True

class Unique(models.Model):
    unique = models.CharField(verbose_name='Unique String', max_length=36, default=UniqueStr)

    class Meta:
        abstract = True

class Project(Created, Updated, RemoteRoot, Task):
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

    def get_apiupdate_url(self):
        return reverse('project:api_update', kwargs={'pk': self.id})

def CreateUserProject(user):
    proj = Project.objects.create(created_by=user, updated_by=user, title=user.username + 'Project')
    proj.member.add(user)
    proj.save()
    return proj

class Prefix(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    prefix = models.CharField(verbose_name='Prefix', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.prefix

    def title(self):
        return self.prefix

    def get_list_url(self):
        return reverse('project:prefix_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('project:prefix_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('project:prefix_update', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('project:api_prefix_update', kwargs={'pk': self.id})

class PrefixPtr(models.Model):
    prefix = models.CharField(verbose_name='Prefix', max_length=36, blank=True)
    default_prefix = ''

    def prefix_display(self):
        try:
            return Prefix.objects.get(unique=self.prefix).prefix
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
    pass
