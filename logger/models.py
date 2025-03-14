from django.db import models
from project.models import Project, Created, Updated, Remote
from django.urls import reverse

class Logger(Created, Updated, Remote):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    host = models.CharField(verbose_name='Host', default='127.0.0.1', max_length=100)
    port = models.PositiveSmallIntegerField(verbose_name='Port', default=6379)
    database = models.PositiveSmallIntegerField(verbose_name='Database', default=0)
    password = models.CharField(verbose_name='Password', max_length=32, blank=True)
    interval = models.FloatField(verbose_name='Refresh Interval', default=1)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('logger:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('logger:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('logger:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('logger:delete', kwargs={'pk': self.id})
