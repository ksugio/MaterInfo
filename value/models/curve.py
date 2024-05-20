from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from value.models.filter import Filter
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Curve(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    CategoryChoices = ((0, 'process'), (1, 'structure'), (2, 'property'), (3, 'performance'))
    category = models.PositiveSmallIntegerField(verbose_name='Category', choices=CategoryChoices, default=0)
    template = models.BooleanField(verbose_name='Template', default=False)
    columnx = models.CharField(verbose_name='Column X', max_length=50)
    columny = models.CharField(verbose_name='Column Y', max_length=50)
    startid = models.PositiveIntegerField(verbose_name='Start Index', blank=True, null=True)
    endid = models.PositiveIntegerField(verbose_name='End Index', blank=True, null=True)
    params = models.TextField(verbose_name='Parameters', blank=True)
    alias = models.IntegerField(verbose_name='Alias ID', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('value:curve_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('value:curve_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('value:curve_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('value:curve_delete', kwargs={'pk': self.id})

    def get_plot_url(self):
        return reverse('value:curve_plot', kwargs={'pk': self.id})

    def pathname(self):
        return '%s/%s/%s' % (self.upper.upper.upper, self.upper.upper, self.upper)

    def get_lmmodel(self):
        if self.alias:
            upper = Curve.objects.get(pk=self.alias)
        else:
            upper = self
        cls = import_string('value.models.equation.Equation')
        equations = cls.objects.filter(upper=upper)
        lmmodels = []
        for eq in equations:
            lmmodels.append(eq.lmmodel())
        if lmmodels:
            lmmodel = lmmodels[0]
            for lmm in lmmodels[1:]:
                lmmodel += lmm
            return equations, lmmodel
        else:
            return equations, None

    def get_xy(self):
        df = self.upper.check_read_csv()
        if df is None:
            return None, None
        st = 0
        ed = df.shape[0]
        if self.startid and self.startid > 0:
            st = self.startid
        if self.endid and self.endid < df.shape[0]:
            ed = self.endid
        if self.columnx in df and self.columny in df:
            x = df[st:ed][self.columnx].values
            y = df[st:ed][self.columny].values
            return x, y
        return None, None

    def measure(self):
        x, y = self.get_xy()
        if x is None or y is None:
            return
        equations, lmmodel = self.get_lmmodel()
        if lmmodel:
            params = lmmodel.make_params()
            for eq in equations:
                params = eq.set_params(params)
            try:
                result = lmmodel.fit(y, params, x=x, nan_policy='omit')
                rparams = result.params.valuesdict()
                rparams['RedChi2'] = result.redchi
                self.params = json.dumps(rparams)
            except:
                self.params = ''
        else:
            self.params = ''

    def plot(self, **kwargs):
        x, y = self.get_xy()
        if x is None or y is None:
            return
        plt.plot(x, y, '.')
        plt.xlabel(self.columnx)
        plt.ylabel(self.columny)
        equations, lmmodel = self.get_lmmodel()
        if lmmodel and self.params:
            params = json.loads(self.params)
            params = lmmodel.make_params(**params)
            y_eval = lmmodel.eval(params, x=x)
            plt.plot(x, y_eval)

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
        elif self.params == '':
            return {}
        else:
            upper_feature = self.upper.feature()
            params = json.loads(self.params)
            params = self.prefix_add(params)
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': self.get_category_display(),
                **params
            }


