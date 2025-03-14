from django.db import models
from django.urls import reverse
from django.utils import timezone
from project.models import Created, Updated, RemoteRoot, Remote, Project
import datetime

class Calendar(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('calendars:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        today = datetime.date.today()
        return reverse('calendars:detail', kwargs={'pk': self.id, 'year': today.year, 'month': today.month})

    def get_update_url(self):
        return reverse('calendars:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('calendars:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('calendars:api_update', kwargs={'pk': self.id})

def Timenow():
    tp = timezone.now() + datetime.timedelta(minutes=30)
    return tp.replace(minute=0, second=0, microsecond=0)

class Plan(Created, Updated, Remote):
    upper = models.ForeignKey(Calendar, verbose_name='Calendar', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    start = models.DateTimeField(verbose_name='Start', default=Timenow)
    finish = models.DateTimeField(verbose_name='Finish', default=Timenow)
    note = models.TextField(verbose_name='Note', blank=True)
