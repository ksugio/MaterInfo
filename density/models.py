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

    def get_apiupdate_url(self):
        return reverse('density:api_update', kwargs={'pk': self.id})

    def recent_updated_at(self):
        return self.updated_at

    def relative_density(self):
        if self.unit == 2:
            return self.measured
        elif self.theoretical:
            return self.measured / self.theoretical()
        else:
            return None

    def theoretical(self):
        material = Material.objects.filter(upper=self)
        if len(material) == 0:
            return 1.0
        nc = 0
        tot = 0.0
        for mat in material:
            if mat.fraction is not None:
                tot += mat.fraction
            else:
                nc += 1
        if nc > 0:
            res = (100.0 - tot) / nc
        else:
            res = 0.0
        density = 0
        for mat in material:
            if mat.fraction is not None:
                density += mat.fraction / 100 * mat.density
            else:
                density += res / 100 * mat.density
        return density

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
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'property',
                prefix+'_SI': self.unit_density(0),
                prefix+'_CGS': self.unit_density(1),
                prefix+'_RD': self.unit_density(2)
            }

class Material(Updated, Remote):
    upper = models.ForeignKey(Density, verbose_name='Material', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=100)
    density = models.FloatField(verbose_name='Density')
    fraction = models.FloatField(verbose_name='Fraction', blank=True, null=True)

    def __str__(self):
        return self.name

    def title(self):
        return '%s : %s' % (self.upper.title, self.name)

    def get_detail_url(self):
        return reverse('density:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('density:material_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('density:material_delete', kwargs={'pk': self.id})
