from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote
from .classification import Classification
from .classification_lib import TrainModel
from .regression_lib import HParam2Dict
from sklearn.model_selection import train_test_split
import numpy as np
import json
import shap

class ClassSHAP(Created, Updated, Remote):
    upper = models.ForeignKey(Classification, verbose_name='Classification', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    test_size = models.FloatField(verbose_name='Test Size', default=0.2)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:classshap_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:classshap_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:classshap_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:classshap_delete', kwargs={'pk': self.id})

    def explain(self):
        features, obj = self.upper.transformed_dataset()
        x_train, x_test, y_train, y_test = train_test_split(features, obj, test_size=self.test_size)
        dparam = HParam2Dict(self.upper.hparam)
        method = self.upper.method
        model = TrainModel(x_train, y_train, dparam, method)
        if method == 0 or method == 1:
            explainer = shap.LinearExplainer(model, x_train)
        elif method == 5 or method == 10 or method == 11:
            explainer = shap.TreeExplainer(model)
        elif method == 7 or method == 8:
            summary = shap.kmeans(x_train, 10)
            explainer = shap.KernelExplainer(model.predict, summary)
        else:
            summary = shap.kmeans(x_train, 10)
            explainer = shap.KernelExplainer(model.predict_proba, summary)
        shap_values = explainer.shap_values(X=x_test)
        shap_values = np.array(shap_values)
        targets = list(set(obj))
        results = {
            'shap_values': shap_values.tolist(),
            'x_test': x_test.values.tolist(),
            'columns': features.columns.values.tolist(),
            'targets': targets
        }
        self.results = json.dumps(results)

    def plot(self, **kwargs):
        results = json.loads(self.results)
        if np.array(results['shap_values']).ndim == 2:
            shap_values = np.array(results['shap_values'])
        else:
            shap_values = []
            for value in results['shap_values']:
                shap_values.append(np.array(value))
        x_test = np.array(results['x_test'])
        columns = results['columns']
        targets = results['targets']
        shap.summary_plot(shap_values, x_test, plot_type="bar",
                          feature_names=columns, class_names=targets, show=False)

