from django.db import models
from django.urls import reverse
from django.utils.module_loading import import_string
from project.models import Created, Updated, RemoteRoot, Task, Project

class Sample(Created, Updated, RemoteRoot, Task):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    design = models.CharField(verbose_name='Design', max_length=36, blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('sample:list', kwargs={'pk': self.upper.id, 'order': 0, 'size': 0})

    def get_detail_url(self):
        return reverse('sample:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('sample:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('sample:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('sample:api_update', kwargs={'pk': self.id})

    def get_experiment(self):
        cls = import_string('design.models.experiment.Experiment')
        experiment = cls.objects.filter(unique=self.design)
        if experiment:
            return experiment[0]
        else:
            return None

    def get_condition(self):
        experiment = self.get_experiment()
        if experiment:
            return experiment.get_condition()
        else:
            return {}

    def designid(self):
        experiment = self.get_experiment()
        if experiment:
            return experiment.id
        else:
            return None

    def feature(self):
        return {
            'Project_id': self.upper.id,
            'Project_title': self.upper.title,
            'Sample_id': self.id,
            'Sample_title': self.title,
            'Upper_id': self.id
        }
