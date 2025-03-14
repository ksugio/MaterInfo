from django.db import models
from django.urls import reverse
from project.models import Updated, Remote, Unique
from sample.models import Sample
from .design import Design
import numpy as np
import pandas as pd
import json
import GPyOpt
import random

AcquisitionChoices = ((0, 'EI'), (1, 'MPI'), (2, 'LCB'))

class Experiment(Updated, Remote, Unique):
    upper = models.ForeignKey(Design, verbose_name='Design', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    condition = models.TextField(verbose_name='Condition', blank=True)
    property = models.FloatField(verbose_name='Property', blank=True, null=True)
    note = models.TextField(verbose_name='Note', blank=True)

    def get_list_url(self):
        return reverse('design:experiment_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('design:experiment_list', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('design:experiment_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('design:experiment_delete', kwargs={'pk': self.id})

    def set_condition(self, dispcond):
        try:
            columns = json.loads(self.upper.columns)
            columns = { v: k for k, v in columns.items() }
            cond = json.loads(dispcond)
            newcond = {}
            for key, value in cond.items():
                newcond[columns[key]] = value
            self.condition = json.dumps(newcond)
        except:
            pass

    def get_condition(self):
        try:
            cond = json.loads(self.condition)
            columns = json.loads(self.upper.columns)
            newcond = {}
            for key, value in cond.items():
                    newcond[columns[key]] = value
            return newcond
        except:
            return ''

    def set_model_property(self):
        if self.upper.modelfunc:
            try:
                cond = self.get_condition()
                df = pd.Series(cond).to_frame().T
                self.property = df.eval(self.upper.modelfunc)[0]
            except:
                return

    def set_random_condition(self, df):
        ran = random.randint(1, df.shape[0])
        cond = df.iloc[ran - 1].to_dict()
        self.condition = json.dumps(cond, indent=2)

    def doptimal(self):
        df = self.upper.read_csv()
        edf = self.upper.get_experiments()
        if df is None or edf is None:
            self.set_random_condition(df)
            return
        edf.pop('Property')
        all = pd.concat([edf, df]).drop_duplicates()
        df = all[edf.shape[0]:]
        std_all = (all - all.mean()) / all.std()
        std_df = std_all[edf.shape[0]:]
        std_edf = std_all[:edf.shape[0]]
        base = std_edf.values.tolist()
        maxd = 0.0
        maxid = -1
        for i in range(len(std_df)):
            X = np.array(base + [list(std_df.iloc[i])])
            d = np.linalg.det(X.T @ X)
            if d > maxd:
                maxd = d
                maxid = i
        if maxid >= 0:
            cond = df.iloc[maxid].to_dict()
            self.condition = json.dumps(cond, indent=2)
            note = 'Method : D_Optimal\nMaxD : %e' % (maxd)
            if self.note:
                self.note += '\n' + note
            else:
                self.note = note
        else:
            self.set_random_condition(df)

    def bayesian(self, target, acquisition):
        df = self.upper.read_csv()
        edf = self.upper.get_experiments()
        if df is None or edf is None:
            self.set_random_condition(df)
            return
        edf = edf.dropna()
        props = edf.pop('Property').values
        if len(props) <= 1:
            self.set_random_condition(df)
            return
        obj = (props - target) ** 2
        domain = []
        for col in df.columns:
            domain.append({
                'name': col,
                'type': 'discrete',
                'domain': tuple(np.sort(np.unique(df[col].values)))
            })
        acquisition_type = AcquisitionChoices[acquisition][1]
        params = {
            'f': None,
            'domain': domain,
            'X': edf.values,
            'Y': obj.reshape((-1, 1)),
            'model_type': 'GP',
            'acquisition': acquisition_type,
            'de_duplication': True,
            "normalize_Y": True,
            "exact_feval": False
        }
        bo = GPyOpt.methods.BayesianOptimization(**params)
        sugg = bo.suggest_next_locations(ignored_X=edf.values)
        pred = bo.model.model.predict(sugg)
        cond = {}
        for i in range(len(sugg[0])):
            cond[domain[i]['name']] = sugg[0][i]
        self.condition = json.dumps(cond, indent=2)
        note = 'Method : Bayesian\nTarget : %f\nAcquisition : %s\nPredict Mean : %f\nPredict Var. : %f' % (target, acquisition_type, pred[0], pred[1])
        if self.note:
            self.note += '\n' + note
        else:
            self.note = note

    def sampleid(self):
        sample = Sample.objects.filter(design=self.unique)
        if sample:
            return sample[0].id
        else:
            return None

    def feature(self):
        if self.upper.status:
            return {}
        cond = self.get_condition()
        dic = {
            'Project_id': self.upper.upper.id,
            'Project_title': self.upper.upper.title,
            'Upper_id': self.upper.id,
            'Model': self.__class__.__name__,
            'Model_id': self.id,
            'Category': 'process',
            **cond
        }
        if self.property is not None:
            dic[self.upper.prefix_display()] = self.property
        sample = Sample.objects.filter(design=self.unique)
        if sample:
            dic['Sample_id'] = sample[0].id
            dic['Sample_title'] = sample[0].title
        return dic


