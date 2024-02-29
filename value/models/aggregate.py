from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from value.models.filter import Filter
import pandas as pd

class Aggregate(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    CategoryChoices = ((0, 'process'), (1, 'structure'), (2, 'property'), (3, 'performance'))
    category = models.PositiveSmallIntegerField(verbose_name='Category', choices=CategoryChoices, default=0)
    column = models.CharField(verbose_name='Column', max_length=50)
    mean = models.FloatField(verbose_name='Mean', blank=True, null=True)
    std = models.FloatField(verbose_name='STD', blank=True, null=True)
    min = models.FloatField(verbose_name='Min', blank=True, null=True)
    median = models.FloatField(verbose_name='Median', blank=True, null=True)
    max = models.FloatField(verbose_name='Max', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('value:aggregate_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('value:aggregate_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('value:aggregate_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('value:aggregate_delete', kwargs={'pk': self.id})

    def pathname(self):
        return '%s/%s/%s' % (self.upper.upper.upper, self.upper.upper, self.upper)

    def measure(self):
        df = self.upper.check_read_csv()
        if df is None:
            return
        dat = df[self.column]
        self.mean = dat.mean()
        self.std = dat.std()
        self.min = dat.min()
        self.median = dat.median()
        self.max = dat.max()

    def upper_updated(self):
        return self.updated_at < self.upper.recent_updated_at()

    def upper_updated_measure(self):
        if self.upper_updated():
            self.measure()
            self.save()
            return True
        else:
            return False

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status or self.upper.upper.upper.status:
            return {}
        else:
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': self.get_category_display(),
                prefix+'_mean': self.mean,
                prefix+'_std': self.std,
                prefix+'_min': self.min,
                prefix+'_median': self.median,
                prefix+'_max': self.max
            }
