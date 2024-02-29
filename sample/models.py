from django.db import models
from django.urls import reverse
from project.models import Created, Updated, RemoteRoot, Project

class Sample(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('sample:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('sample:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('sample:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('sample:delete', kwargs={'pk': self.id})

