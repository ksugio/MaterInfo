from django.db import models
from django.utils.module_loading import import_string
from django.urls import reverse
from django.utils import timezone
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from .collect import Collect, HeadColumns
from io import BytesIO
import os
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def FilterUploadTo(instance, filename):
    return filename

class Filter(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Collect, verbose_name='Collect', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    disp_head = models.PositiveIntegerField(verbose_name='Display Head', default=50)
    disp_tail = models.PositiveIntegerField(verbose_name='Display Tail', default=50)
    hist_bins = models.PositiveIntegerField(verbose_name='Histgram Bins', default=10)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)
    columns_text = models.TextField(verbose_name='Columns Text', blank=True)
    describe = models.TextField(verbose_name='Describe', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:filter_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:filter_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:filter_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:filter_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('collect:filter_table', kwargs={'pk': self.id})

    def process_updated_at(self):
        cls = import_string('collect.models.process.Process')
        updated_at = self.upper.updated_at
        processes = cls.objects.filter(upper=self)
        for process in processes:
            if process.updated_at > updated_at:
                updated_at = process.updated_at
        return updated_at

    def recent_updated_at(self):
        updated_at = self.process_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('CollectFilter.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def check_read_csv(self):
        if self.updated_at < self.process_updated_at():
            df = self.upper.read_csv()
            df, kwargs = self.procval(df)
            self.save_csv(df)
            self.save()
            return df
        else:
            return self.read_csv()

    def procval(self, df, procid=0):
        cls = import_string('collect.models.process.Process')
        processes = cls.objects.filter(upper=self).order_by('order')
        kwargs = {}
        for process in processes:
            df, kwargs = process.process(df, **kwargs)
            if process.id == procid:
                break
        return df, kwargs

    def savefile(self):
        df = self.upper.read_csv()
        df, kwargs = self.procval(df)
        columns = list(df.columns.values)
        self.columns_text = ','.join(columns)
        self.save_csv(df)
        df = self.upper.drophead(df)
        self.describe = df.describe().to_json()

    def disp_table(self, **kwargs):
        df = self.read_csv()
        hdf = df.isnull().any().to_frame(name='IsNull').T
        df = pd.concat([hdf, df])
        ldf = df.isnull().any(axis=1).to_frame(name='IsNull')
        ldf.loc['IsNull'] = hdf.sum(axis=1) > 0
        df = pd.concat([ldf, df], axis=1)
        if df is not None and self.disp_head + self.disp_tail < df.shape[0]:
            return pd.concat([df.head(self.disp_head), df.tail(self.disp_tail)])
        else:
            return df

    def columns_choice(self, drophead=False):
        columns = self.columns_text.split(',')
        if drophead:
            for name, val in HeadColumns:
                if name in columns:
                    columns.remove(name)
        choice = []
        for item in columns:
            choice.append((item, item))
        return choice

    def plot(self, **kwargs):
        df = self.read_csv()
        if df is None:
            return
        name = kwargs['name']
        if name in df:
            fig, ax = plt.subplots()
            ax.hist(df[name], bins=self.hist_bins, edgecolor="black")
            ax.set_xlabel(name)
            ax.set_ylabel('Frequency')
            return fig
