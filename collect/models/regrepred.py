from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo
from .regression import Regression, RunONNX
from .collect import HeadColumns
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np
import pandas as pd
import json

class RegrePred(Created, Updated, Remote):
    upper = models.ForeignKey(Regression, verbose_name='Regression', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo)
    objective = models.CharField(verbose_name='Objective column', max_length=250, blank=True)
    drop = models.CharField(verbose_name='Drop columns', max_length=250, blank=True)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:regrepred_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:regrepred_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:regrepred_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:regrepred_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('collect:regrepred_table', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_regrepred_update', kwargs={'pk': self.id})

    def predict(self):
        if not self.file:
            return
        with self.file.open('r') as f:
            df = pd.read_csv(f)
        if self.objective in df.columns.values:
            objective = df.pop(self.objective)
        else:
            objective = None
        cols = []
        for item in HeadColumns:
            if item[0] in df.columns:
                cols.append(item[0])
        df = df.drop(columns=cols)
        ldrop = self.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        cols = []
        for col in ldrop:
            if col in df.columns:
                cols.append(col)
        df = df.drop(columns=cols)
        if self.upper.file2_type == 0:
            model = self.upper.read_model()
            if model.n_features_in_ == df.shape[1]:
                pred = model.predict(df.values)
            else:
                pred = None
        elif self.upper.file2_type == 1:
            onxs = self.upper.read_model(raw_data=True)
            pred = RunONNX(onxs, df.values)
        if pred is not None:
            if objective is not None:
                results = {
                    'pred': pred.tolist(),
                    'r2': r2_score(objective, pred),
                    'rmse': np.sqrt(mean_squared_error(objective, pred)),
                    'mae': mean_absolute_error(objective, pred)
                }
            else:
                results = {
                    'pred': pred.tolist()
                }
            self.results = json.dumps(results)
        else:
            self.results = ''

    def disp_table(self, **kwargs):
        if not self.file:
            return None
        with self.file.open('r') as f:
            df = pd.read_csv(f)
        if self.results:
            results = json.loads(self.results)
            df['Predict'] = results['pred']
        return df
