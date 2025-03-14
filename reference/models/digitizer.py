from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Unique, ModelUploadTo
from .image import Image
from io import BytesIO
import json
import pandas as pd

class Digitizer(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Image, verbose_name='Figure', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    data = models.TextField(verbose_name='JSON Plot Data', blank=True)
    file = models.FileField(verbose_name='CSV file', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:digitizer_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:digitizer_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:digitizer_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:digitizer_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_digitizer_update', kwargs={'pk': self.id})

    def convert(self):
        if not self.data:
            return None, None
        data = json.loads(self.data)
        if 'axis' in data and 'plot' in data:
            axis = data['axis']
            if 'XAxis' in axis and 'YAxis' in axis and len(axis['XAxis']) == 2 and len(axis['YAxis']) == 2:
                lx = axis['XAxis'][1][0] - axis['XAxis'][0][0]
                ly = axis['YAxis'][1][1] - axis['YAxis'][0][1]
            else:
                return None, None
            plot = data['plot']
            conv = {}
            for key in plot.keys():
                vx = []
                vy = []
                for x, y in plot[key]:
                    dx = x - axis['XAxis'][0][0]
                    dy = y - axis['YAxis'][0][1]
                    vx.append(dx / lx * (axis['X2'] - axis['X1']) + axis['X1'])
                    vy.append(dy / ly * (axis['Y2'] - axis['Y1']) + axis['Y1'])
                conv[key] = [vx, vy]
            return conv, axis
        else:
            return None, None

    def get_df(self):
        conv, axis = self.convert()
        if conv is not None:
            max_len = 0
            for key in conv.keys():
                if len(conv[key][0]) > max_len:
                    max_len = len(conv[key][0])
                if len(conv[key][1]) > max_len:
                    max_len = len(conv[key][1])
            df = pd.DataFrame()
            for key in conv.keys():
                if len(conv[key][0]) < max_len:
                    for i in range(max_len - len(conv[key][0])):
                        conv[key][0].append(None)
                if len(conv[key][1]) < max_len:
                    for i in range(max_len - len(conv[key][1])):
                        conv[key][1].append(None)
                df[key + '_x'] = conv[key][0]
                df[key + '_y'] = conv[key][1]
            return df
        else:
            return pd.DataFrame()

    def save_csv(self):
        df = self.get_df()
        buf = BytesIO()
        df.to_csv(buf, mode="wb", encoding="UTF-8", index=False)
        self.file.save('Digitizer.csv', buf)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def disp_table(self, **kwargs):
        if self.file:
            return self.read_csv()

    # def plot(self, **kwargs):
    #     conv, axis = self.convert()
    #     if conv is not None:
    #         for key in conv.keys():
    #             plt.plot(conv[key][0], conv[key][1], "-o", label=key)
    #         plt.xlabel(axis['XTitle'])
    #         plt.ylabel(axis['YTitle'])
    #         plt.legend()
