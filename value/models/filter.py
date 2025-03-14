from django.db import models
from django.utils.module_loading import import_string
from django.urls import reverse
from django.utils import timezone
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from plot.models.item import ColorChoices
from .value import Value
from io import StringIO, BytesIO
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Filter(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Value, verbose_name='Value', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    template = models.BooleanField(verbose_name='Template', default=False)
    disp_head = models.PositiveIntegerField(verbose_name='Display Head', default=50)
    disp_tail = models.PositiveIntegerField(verbose_name='Display Tail', default=50)
    alias = models.IntegerField(verbose_name='Alias ID', blank=True, null=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('value:filter_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('value:filter_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('value:filter_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('value:filter_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('value:filter_table', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('value:api_filter_update', kwargs={'pk': self.id})

    def entity_id(self):
        if self.alias:
            return self.alias
        else:
            return self.id

    def process_updated_at(self):
        cls = import_string('value.models.process.Process')
        updated_at = self.upper.updated_at
        if self.alias:
            source = Filter.objects.get(pk=self.alias)
            processes = cls.objects.filter(upper=source)
            for process in processes:
                if process.updated_at > updated_at:
                    updated_at = process.updated_at
        else:
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
        filename = '%s%s.csv' % (self.upper.__class__.__name__, self.__class__.__name__)
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        self.file.save(filename, buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def check_read_csv(self):
        if self.updated_at < self.process_updated_at():
            self.savefile()
            self.save()
        return self.read_csv()

    def procval(self, df, procid=0):
        cls = import_string('value.models.process.Process')
        if self.alias:
            source = Filter.objects.get(pk=self.alias)
            processes = cls.objects.filter(upper=source).order_by('order')
        else:
            processes = cls.objects.filter(upper=self).order_by('order')
        for process in processes:
            df = process.process(df)
            if process.id == procid:
                break
        return df

    def savefile(self):
        df = self.upper.read_data()
        df = self.procval(df)
        self.save_csv(df)

    def disp_table(self, **kwargs):
        df = self.read_csv()
        if self.disp_head + self.disp_tail < df.shape[0]:
            return pd.concat([df.head(self.disp_head), df.tail(self.disp_tail)])
        else:
            return df

    def feature(self):
        return {
            'Project_id': self.upper.upper.upper.id,
            'Project_title': self.upper.upper.upper.title,
            'Sample_id': self.upper.upper.id,
            'Sample_title': self.upper.upper.title,
            'Value_id': self.upper.id,
            'Value_title': self.upper.title,
            'Upper_id': self.entity_id(),
        }


    # def get_xy(self, columnx, columny, df):
    #     if columnx >=0 and columnx < df.shape[1]:
    #         x = df.iloc[:,columnx]
    #     else:
    #         x = df.index.values
    #     if columny >= 0 and columny < df.shape[1]:
    #         y = df.iloc[:,columny]
    #     else:
    #         y = df.index.values
    #     return x, y

    # def plot(self, df):
    #     if self.alias:
    #         model = Filter.objects.get(pk=self.alias)
    #     else:
    #         model = self
    #     if model.display == 0:
    #         return
    #     elif model.display == 1:
    #         x, y = self.get_xy(model.columnx, model.columny, df)
    #         plt.plot(x, y, color=model.get_color_display())
    #         plt.xlabel('Column %d' % model.columnx)
    #         plt.ylabel('Column %d' % model.columny)
    #     elif model.display == 2:
    #         x, y = self.get_xy(model.columnx, model.columny, df)
    #         plt.hist(x, color=model.get_color_display(), bins=model.bins)
    #         plt.xlabel('Column %d' % model.columnx)
