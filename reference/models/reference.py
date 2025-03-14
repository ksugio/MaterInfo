from django.db import models
from django.urls import reverse
from project.models import Created, Updated, RemoteRoot, Project

default_template = '[{{ id }}] {{ author }}, "{{ title }}", {{ journal }}, Vol. {{ volume }}{% if number %}, {{ number }}{% endif %} ({{ year }}) pp. {{ pages }}{% if doi %}, {{ doi }}{% endif %}'

class Reference(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    OrderChoices = ((0, 'Latest Create'), (1, 'Earliest Create'), (2, 'Latest Update'), (3, 'Earliest Update'),
                    (4, 'Latest'), (5, 'Earliest'), (6, 'Aescending Key'), (7, 'Descending Key'))
    order = models.PositiveSmallIntegerField(verbose_name='Order', choices=OrderChoices, default=0)
    PageSizeChoices = ((0, '10'), (1, '20'), (2, '50'), (3, '100'), (4, '200'), (5, '500'))
    pagesize = models.PositiveSmallIntegerField(verbose_name='Default Page Size', choices=PageSizeChoices, default=0)
    template = models.TextField(verbose_name='Template', default=default_template)
    startid = models.PositiveSmallIntegerField(verbose_name='Start ID', default=1)
    data = models.TextField(verbose_name='Data', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_update', kwargs={'pk': self.id})
