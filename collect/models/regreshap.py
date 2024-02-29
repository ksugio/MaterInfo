import pandas as pd
from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote
from .regression import Regression
from .regression_lib import HParam2Dict, TrainModel
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import json
import shap

class RegreSHAP(Created, Updated, Remote):
    upper = models.ForeignKey(Regression, verbose_name='Regression', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    test_size = models.FloatField(verbose_name='Test Size', default=0.2)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:regreshap_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:regreshap_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:regreshap_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:regreshap_delete', kwargs={'pk': self.id})

    def explain(self):
        features, obj = self.upper.transformed_dataset()
        x_train, x_test, y_train, y_test = train_test_split(features, obj, test_size=self.test_size)
        dparam = HParam2Dict(self.upper.hparam)
        method = self.upper.method
        model = TrainModel(x_train, y_train, dparam, method)
        if method == 0 or method == 1 or method == 2 or method == 3:
            explainer = shap.LinearExplainer(model, x_train)
        elif method == 6 or method == 7 or method == 10 or method == 11:
            explainer = shap.TreeExplainer(model)
        else:
            summary = shap.kmeans(x_train, 10)
            explainer = shap.KernelExplainer(model.predict, summary)
        shap_values = explainer.shap_values(X=x_test)
        results = {
            'shap_values': shap_values.tolist(),
            'x_test': x_test.values.tolist(),
            'columns': features.columns.values.tolist()
        }
        self.results = json.dumps(results)

    def plot(self, **kwargs):
        results = json.loads(self.results)
        shap_values = np.array(results['shap_values'])
        x_test = np.array(results['x_test'])
        columns = results['columns']
        shap.summary_plot(shap_values, x_test, feature_names=columns, show=False)

    def plot_dependence(self, **kwargs):
        ind = kwargs['name']
        results = json.loads(self.results)
        shap_values = np.array(results['shap_values'])
        x_test = np.array(results['x_test'])
        columns = results['columns']
        if ind in columns:
            shap.dependence_plot(ind, shap_values, x_test, feature_names=columns, show=False)
