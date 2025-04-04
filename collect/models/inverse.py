from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Task, ModelUploadTo, Unique
from .filter import Filter
from .regression import Regression
from io import BytesIO
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Inverse(Created, Updated, Remote, Task, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    regression1 = models.CharField(verbose_name='Regression 1', max_length=36, blank=True)
    target1 = models.FloatField(verbose_name='Target value 1', default=0.0)
    regression2 = models.CharField(verbose_name='Regression 2', max_length=36, blank=True)
    target2 = models.FloatField(verbose_name='Target value 2', default=0.0)
    regression3 = models.CharField(verbose_name='Regression 3', max_length=36, blank=True)
    target3 = models.FloatField(verbose_name='Target value 3', default=0.0)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=100)
    seed = models.IntegerField(verbose_name='Seed of sampler', default=0)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:inverse_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:inverse_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:inverse_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:inverse_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('collect:inverse_table', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_inverse_update', kwargs={'pk': self.id})

    def save_csv(self, df, save=False):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Inverse.csv', buf, save=save)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def get_regression1(self):
        return Regression.objects.get(unique=self.regression1)

    def get_regression2(self):
        return Regression.objects.get(unique=self.regression2)

    def get_regression3(self):
        return Regression.objects.get(unique=self.regression3)

    def regression_data(self):
        df = self.upper.check_read_csv()
        if df is None:
            return None, None
        features = self.upper.upper.drophead(df)
        suggests = []
        for col in features.columns:
            suggests.append({
                'name': col,
                'min': float(features[col].min()),
                'max': float(features[col].max())
            })
        regdata = []
        # Regression 1
        model1 = self.get_regression1()
        regd = {
            'objective': model1.objective,
            'drop':  model1.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(','),
            'target': self.target1,
            'model': model1.read_model(raw_data=True),
            'type': model1.file2_type
        }
        regdata.append(regd)
        # Regression 2
        if self.regression2:
            model2 = self.get_regression2()
            regd = {
                'objective': model2.objective,
                'drop': model2.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(','),
                'target': self.target2,
                'model': model2.read_model(raw_data=True),
                'type': model2.file2_type
            }
            regdata.append(regd)
        # Regression 3
        if self.regression2 and self.regression3:
            model3 = self.get_regression3()
            regd = {
                'objective': model3.objective,
                'drop': model3.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(','),
                'target': self.target3,
                'model': model3.read_model(raw_data=True),
                'type': model3.file2_type
            }
            regdata.append(regd)
        return regdata, suggests

    def disp_table(self, **kwargs):
        if self.file:
            return self.read_csv()

    def plot(self, **kwargs):
        if not self.file:
            return
        df = self.read_csv()[::-1]
        pred1 = df['_Predict1']
        num = 1
        if '_Predict2' in df:
            pred2 = df['_Predict2']
            num += 1
        if '_Predict3' in df:
            pred3 = df['_Predict3']
            num += 1
        besttrial = df['_BestTrial']
        if num == 1:
            fig, ax = plt.subplots(figsize=(6, 6))
            trialid = df['_TrialID']
            ax.scatter(trialid, pred1, marker='.', c=list(besttrial))
            ax.set_xlabel('Trial ID')
            ax.set_ylabel('Predict 1')
            return fig
        elif num == 2:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.scatter(pred1, pred2, marker='.',  c=list(besttrial))
            ax.set_xlabel('Predict 1')
            ax.set_ylabel('Predict 2')
            return fig
        elif num == 3:
            fig, ax = plt.subplots(1, 3, figsize=(18, 6))
            ax[0].scatter(pred1, pred2,  marker='.',  c=list(besttrial))
            ax[0].set_xlabel('Predict 1')
            ax[0].set_ylabel('Predict 2')
            ax[1].scatter(pred1, pred3,  marker='.',  c=list(besttrial))
            ax[1].set_xlabel('Predict 1')
            ax[1].set_ylabel('Predict 3')
            ax[2].scatter(pred2, pred3,  marker='.',  c=list(besttrial))
            ax[2].set_xlabel('Predict 2')
            ax[2].set_ylabel('Predict 3')
            return fig



