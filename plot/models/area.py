from django.db import models
from project.models import Updated, Remote
from .plot import Plot
from django.urls import reverse

class Area(Updated, Remote):
    upper = models.ForeignKey(Plot, verbose_name='Plot', on_delete=models.CASCADE)
    xlabel = models.CharField(verbose_name='X Label', max_length=100, blank=True)
    ylabel = models.CharField(verbose_name='Y Label', max_length=100, blank=True)
    xmin = models.FloatField(verbose_name='X Min', blank=True, null=True)
    xmax = models.FloatField(verbose_name='X Max', blank=True, null=True)
    ymin = models.FloatField(verbose_name='Y Min', blank=True, null=True)
    ymax = models.FloatField(verbose_name='Y Max', blank=True, null=True)
    LegendChoices = ((0, 'None'), (1, 'Best'), (2, 'UpperRight'), (3, 'UpperLeft'), (4, 'LowerLeft'), (5, 'LowerRight'))
    legend = models.PositiveSmallIntegerField(verbose_name='Legend', choices=LegendChoices, default=0)
    order = models.SmallIntegerField(verbose_name='Order')

    def __str__(self):
        return self.title()

    def title(self):
        return '%s : %s' % (self.upper.title, self.name())

    def name(self):
        return 'Area_%s' % (self.order)

    def get_detail_url(self):
        return reverse('plot:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('plot:area_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('plot:area_delete', kwargs={'pk': self.id})

    def get_plot_url(self):
        return reverse('plot:area_plot', kwargs={'pk': self.id})
