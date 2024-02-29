from django.db import models
from django.urls import reverse
from project.models import Project, Created, Updated

class Repository(Created, Updated):
    upper = models.ForeignKey(Project, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Active'), (1, 'Stable'), (2, 'Stop'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('repository:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('repository:detail', kwargs={'pk': self.id, 'branch': 'master', 'hexsha': 'top'})

    def get_update_url(self):
        return reverse('repository:update', kwargs={'pk': self.id})


