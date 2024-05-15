from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from sample.models import Sample
import pandas as pd

class Hardness(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    UnitChoices = ((0, 'HV'), (1, 'HRC'), (2, 'HB'), (3, 'HRA'), (4, 'HRB'), (5, 'HRD'), (6, 'HS'), (7, 'HRF'), (8, 'HIT'))
    unit = models.PositiveSmallIntegerField(verbose_name='Unit', choices=UnitChoices, default=0)
    load = models.FloatField(verbose_name='Load', blank=True, null=True)
    LoadUnitChoices = ((0, 'gf'), (1, 'kgf'))
    load_unit = models.PositiveSmallIntegerField(verbose_name='Load Unit', choices=LoadUnitChoices, default=0)
    time = models.FloatField(verbose_name='Time(s)', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('hardness:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('hardness:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('hardness:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('hardness:delete', kwargs={'pk': self.id})

    def value_describe(self):
        queryset = Value.objects.filter(upper=self)
        vals = []
        for q in queryset:
            if q.status == 0:
                vals.append(q.value)
        describe = pd.Series(vals).describe()
        if '50%' in describe:
            describe['median'] = describe['50%']
        return describe

    def feature(self):
        if self.status or self.upper.status:
            return {}
        else:
            describe = self.value_describe()
            prefix = self.prefix_display()
            prefixhv = '%s_%s' % (prefix, self.get_unit_display())
            return {
                'Project_id': self.upper.upper.id,
                'Project_title': self.upper.upper.title,
                'Sample_id': self.upper.id,
                'Sample_title': self.upper.title,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'property',
                prefixhv+'_mean': describe['mean'],
                prefixhv+'_std': describe['std'],
                prefixhv+'_min': describe['min'],
                prefixhv+'_median': describe['median'],
                prefixhv+'_max': describe['max']
            }

class Value(Updated, Remote):
    upper = models.ForeignKey(Hardness, verbose_name='Hardness', on_delete=models.CASCADE)
    value = models.FloatField(verbose_name='Value', default=0.0)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)

    def __str__(self):
        return str(self.value)

    def title(self):
        return '%s : Value' % self.upper.title

    def get_detail_url(self):
        return reverse('hardness:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('hardness:value_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('hardness:value_delete', kwargs={'pk': self.id})
