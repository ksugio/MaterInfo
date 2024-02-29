from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from project.models import Created, Updated, RemoteRoot, Remote, Project, UpperModelUploadTo
import os

def ArticleUploadTo(instance, filename):
    return filename

class Article(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Writing'), (1, 'Reviewing'), (2, 'Revising'), (3, 'Finish'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    CategoryChoices = ((0, 'Misc'), (1, 'Report'), (2, 'Thesis'), (3, 'Paper'), (4, 'Conference'), (5, 'Event'), (6, 'Manual'), (7, 'Information'))
    category = models.PositiveSmallIntegerField(verbose_name='Category', choices=CategoryChoices, default=0)
    public = models.BooleanField(verbose_name='Public', default=False)
    text = models.TextField(verbose_name='Text', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('article:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('article:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('article:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('article:delete', kwargs={'pk': self.id})

    def get_public_url(self):
        return reverse('article:public_detail', kwargs={'pk': self.id})

class File(Updated, Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.FileField(verbose_name='File', upload_to=UpperModelUploadTo)

    def get_detail_url(self):
        return reverse('article:update', kwargs={'pk': self.upper.id})

class Diff(Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    diff = models.TextField(verbose_name='Diff')
    updated_by = models.ForeignKey(CustomUser, verbose_name='Updated by', on_delete=models.PROTECT)
    updated_at = models.DateTimeField(verbose_name='Updated at', default=timezone.now)
