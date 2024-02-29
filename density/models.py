from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from sample.models import Sample
import pandas as pd

class Density(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    UnitChoices = ((0, 'SI'), (1, 'CGS'), (2, 'Percent'))
    unit = models.PositiveSmallIntegerField(verbose_name='Unit', choices=UnitChoices, default=0)
    measured = models.FloatField(verbose_name='Measured')
    theoretical = models.FloatField(verbose_name='Theoretical', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('density:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('density:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('density:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('density:delete', kwargs={'pk': self.id})

    def pathname(self):
        return '%s' % (self.upper)

    def recent_updated_at(self):
        return self.updated_at

    def relative_density(self):
        if self.unit == 2:
            return self.measured
        elif self.theoretical:
            return self.measured / self.theoretical
        else:
            return None

    def unit_density(self, unit):
        if unit == 0:
            if self.unit == 0:
                return self.measured
            elif self.unit == 1:
                return self.measured * 1000
        elif unit == 1:
            if self.unit == 0:
                return self.measured / 1000
            elif self.unit == 1:
                return self.measured
        elif unit == 2:
            return self.relative_density()

    def feature(self):
        if self.status or self.upper.status:
            return {}
        else:
            prefix = self.prefix_display()
            return {
                'Project_id': self.upper.upper.id,
                'Project_title': self.upper.upper.title,
                'Sample_id': self.upper.id,
                'Sample_title': self.upper.title,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'property',
                prefix+'_SI': self.unit_density(0),
                prefix+'_CGS': self.unit_density(1),
                prefix+'_Percent': self.unit_density(2)
            }
