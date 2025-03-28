from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Task
from .classification import Classification
import numpy as np
import json
import shap

class ClassSHAP(Created, Updated, Remote, Task):
    upper = models.ForeignKey(Classification, verbose_name='Classification', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    use_kernel = models.BooleanField(verbose_name='Use Kernel Explainer', default=False)
    kmeans = models.PositiveIntegerField(verbose_name='K Means for Kernel Explainer', default=10)
    nsample = models.PositiveIntegerField(verbose_name='N Sample for Kernel Explainer', default=200)
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

    def get_apiupdate_url(self):
        return reverse('collect:api_classshap_update', kwargs={'pk': self.id})

    def plot(self, **kwargs):
        if self.results:
            results = json.loads(self.results)
            if np.array(results['shap_values']).ndim == 2:
                shap_values = np.array(results['shap_values'])
            else:
                shap_values = []
                for value in results['shap_values']:
                    shap_values.append(np.array(value))
                shap_values = np.array(shap_values)
            x_test = np.array(results['x_test'])
            columns = results['columns']
            targets = results['targets']
            shap.summary_plot(shap_values, x_test, plot_type="bar",
                              feature_names=columns, class_names=targets, show=False)

