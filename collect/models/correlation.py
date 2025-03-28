from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from .filter import Filter
from io import BytesIO
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def CorrelationUploadTo(instance, filename):
    return filename

class Correlation(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    MethodChoices = ((0, 'pearson'), (1, 'kendall'), (2, 'spearman'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    drop = models.BooleanField(verbose_name='Drop Same Group', default=True)
    mincorr = models.FloatField(verbose_name='Minimum Correlation', default=0.7)
    sizex = models.FloatField(verbose_name='Size X', default=9.6)
    sizey = models.FloatField(verbose_name='Size Y', default=9.6)
    ColorMapChoices = ((0, 'RdBu'), (1, 'PiYG'), (2, 'PRGn'), (3, 'BrBG'), (4, 'PuOr'),
                       (5, 'RdGy'), (6, 'RdYlBu'), (7, 'RdYlGn'), (8, 'Spectral'),
                       (9, 'coolwarm'), (10, 'bwr'), (11, 'seismic'))
    colormap = models.PositiveSmallIntegerField(verbose_name='Colormap', choices=ColorMapChoices, default=0)
    colorbar = models.BooleanField(verbose_name='Colorbar', default=False)
    annotate = models.BooleanField(verbose_name='Annotate', default=False)
    label = models.CharField(verbose_name='Label', max_length=50, blank=True, null=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_method(self):
        for meth in self.MethodChoices:
            if meth[0] == self.method:
                return meth[1]

    def get_colormap(self):
        for cmap in self.ColorMapChoices:
            if cmap[0] == self.colormap:
                return cmap[1]

    def get_list_url(self):
        return reverse('collect:correlation_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:correlation_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:correlation_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:correlation_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_correlation_update', kwargs={'pk': self.id})


    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, mode="wb", encoding="UTF-8")
        self.file.save('Correlation.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f, index_col=0)
        return None

    def calc_corr(self):
        df = self.upper.check_read_csv()
        if df is None:
            return
        if df.isnull().values.sum() > 0:
            return
        if self.label in df.columns:
            del df[self.label]
        df = self.upper.upper.drophead(df)
        df = df.corr(method=self.get_method())
        if self.drop:
            df = self.drop_same_group(df)
        self.save_csv(df)

    def drop_same_group(self, df):
        features = df.columns.values
        for col in features:
            gcol = col.split('_')[0]
            for ind in features:
                gind = ind.split('_')[0]
                if gcol == gind:
                    df[col][ind] = None
        return df

    def corr_list(self):
        if not self.file:
            return []
        df = self.read_csv()
        num = df.shape[0]
        list = []
        for i in range(num):
            for j in range(i+1, num):
                val = df.iloc[i, j]
                if not np.isnan(val) and abs(val) > self.mincorr:
                    list.append({'feat1': df.index[i], 'feat2': df.index[j], 'corr': val, 'abs': abs(val)})
        list = sorted(list, key=lambda x: x['abs'], reverse=True)
        return list

    def plot_heatmap(self, **kwargs):
        df = self.read_csv()
        if df is None:
            return
        fig, ax = plt.subplots(figsize=(self.sizex, self.sizey))
        sns.heatmap(df, ax=ax, cmap=self.get_colormap(), cbar=self.colorbar,
                    annot=self.annotate, square=True)
        return fig

    def plot_scatter(self, **kwargs):
        df = self.upper.read_csv()
        if df is None:
            return
        if df.isnull().values.sum() > 0:
            return
        feat1 = kwargs['feat1']
        feat2 = kwargs['feat2']
        fig, ax = plt.subplots()
        if self.label in df.columns:
            labels = df[self.label]
            ax.scatter(df[feat1], df[feat2], marker='.', c=list(labels))
        else:
            ax.scatter(df[feat1], df[feat2], marker='.')
        ax.set_xlabel(feat1)
        ax.set_ylabel(feat2)
        return fig
