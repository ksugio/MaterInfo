from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from sample.models import Sample
from io import BytesIO
import pandas as pd
import os

def Num2Alpha(num):
    if num <= 26:
        return chr(64 + num)
    elif num % 26 == 0:
        return Num2Alpha(num // 26 - 1) + chr(90)
    else:
        return Num2Alpha(num // 26) + chr(64 + num % 26)

class DataFile(models.Model):
    file = None
    DelimiterChoices = ((0, 'Comma'), (1, 'Space'), (2, 'Tab'))
    delimiter = models.PositiveSmallIntegerField(verbose_name='Delimiter', choices=DelimiterChoices, default=0)
    EncodingChoices = ((0, 'utf-8'), (1, 'shift-jis'), (2, 'cp932'))
    encoding = models.PositiveSmallIntegerField(verbose_name='Encoding', choices=EncodingChoices, default=0)
    skiprows = models.PositiveSmallIntegerField(verbose_name='Skiprows', default=0)
    skipends = models.PositiveSmallIntegerField(verbose_name='Skipends', default=0)
    header = models.BooleanField(verbose_name='Header', default=False)
    startstring = models.CharField(verbose_name='Start string', max_length=100, blank=True)
    endstring = models.CharField(verbose_name='End string', max_length=100, blank=True)
    sheetname = models.CharField(verbose_name='Sheet name', max_length=100, blank=True)


    class Meta:
        abstract = True

    def delimiter_char(self):
        delimiters = [",", " ", "\t"]
        return delimiters[self.delimiter]

    def file_ext(self):
        fn, ext = os.path.splitext(self.file.name)
        return ext

    def read_data(self):
        ext = self.file_ext()
        if self.header:
            header = self.skiprows
        else:
            header = None
        with self.file.open('rb') as f:
            try:
                if ext == '.csv':
                    df = pd.read_csv(f, sep=self.delimiter_char(), header=header,
                                     encoding=self.get_encoding_display(),
                                     skiprows=self.skiprows, dtype=str)
                elif ext == '.xlsx':
                    if self.sheetname:
                        if self.sheetname.isdecimal():
                            sheetname = int(self.sheetname)
                        else:
                            sheetname = self.sheetname
                    else:
                        sheetname = 0
                    df = pd.read_excel(f, sheet_name=sheetname, header=header,
                                       skiprows=self.skiprows, dtype=str)
                else:
                    return None
            except:
                return None
        if self.skipends > 0:
            df = df[:-self.skipends]
        if not self.header:
            col = []
            for i in df.columns.values:
                col.append(Num2Alpha(i+1))
            df.columns = pd.Index(col)
        if len(self.startstring) > 0:
            bol = (df[0] == self.startstring)
            if bol.sum() > 0:
                start = df[bol].index[0] + 1
            else:
                start = 0
        else:
            start = 0
        if len(self.endstring) > 0:
            bol = (df[0] == self.endstring)
            if bol.sum() > 0:
                end = df[bol].index[0]
            else:
                end = len(df)
        else:
            end = len(df)
        df = df[start:end].reset_index(drop=True)
        df = df.dropna(how='all')
        for col in df.columns.values:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

def ValueUploadTo(instance, filename):
    return filename

class Value(Created, Updated, Remote, Unique, DataFile):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.FileField(verbose_name='Value file (.csv, .xlsx)', upload_to=ModelUploadTo)
    DataTypeChoices = ((0, 'General'), (1, 'SSCureve'), (2, 'XRD'), (3, 'DSC'))
    datatype = models.PositiveSmallIntegerField(verbose_name='Data type', choices=DataTypeChoices, default=0)
    disp_head = models.PositiveIntegerField(verbose_name='Display Head', default=50)
    disp_tail = models.PositiveIntegerField(verbose_name='Display Tail', default=50)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('value:list', kwargs={'pk': self.upper.id, 'order': 0, 'size': 0})

    def get_detail_url(self):
        return reverse('value:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('value:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('value:delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('value:table', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('value:api_update', kwargs={'pk': self.id})

    def disp_table(self, **kwargs):
        df = self.read_data()
        if df is not None and self.disp_head + self.disp_tail < df.shape[0]:
            return pd.concat([df.head(self.disp_head), df.tail(self.disp_tail)])
        else:
            return df