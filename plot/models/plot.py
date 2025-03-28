from django.db import models
from project.models import Project, Created, Updated, Remote, ModelUploadTo, Unique
from django.urls import reverse

class Plot(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    ncol = models.PositiveSmallIntegerField(verbose_name='N Column', default=1)
    sizex = models.FloatField(verbose_name='Size X', default=6.4)
    sizey = models.FloatField(verbose_name='Size Y', default=4.8)
    FormatChoices = ((0, 'SVG'), (1, 'PNG'), (2, 'JPEG'), (3, 'PDF'), (4, 'EPS'))
    format = models.PositiveSmallIntegerField(verbose_name='Format', choices=FormatChoices, default=0)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('plot:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('plot:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('plot:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('plot:delete', kwargs={'pk': self.id})

    def get_plot_url(self):
        return reverse('plot:plot', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('plot:api_update', kwargs={'pk': self.id})
