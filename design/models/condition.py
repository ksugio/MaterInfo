from django.db import models
from django.urls import reverse
from project.models import Updated, Remote, PrefixPtr
from .design import Design
import random
import numpy as np

class Condition(Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Design, verbose_name='Design', on_delete=models.CASCADE)
    ModeChoices = ((0, 'List'),  (1, 'Linspace'), (2, 'Continuous'),)
    mode = models.PositiveSmallIntegerField(verbose_name='Mode', choices=ModeChoices, default=0)
    values = models.CharField(verbose_name='Values', max_length=256)

    def title(self):
        return '%s : %s' % (self.upper.title, self.prefix_display())

    def get_detail_url(self):
        return reverse('design:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('design:condition_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('design:condition_delete', kwargs={'pk': self.id})

    def candidates(self, num):
        cand = []
        if self.mode == 0:
            cond = [float(c) for c in self.values.split(',')]
            for i in range(num):
                cand.append(random.choice(cond))
            return cand
        elif self.mode == 1:
            param = self.values.split(',')
            cond = np.linspace(float(param[0]), float(param[1]), int(param[2])).tolist()
            for i in range(num):
                cand.append(random.choice(cond))
            return cand
        elif self.mode == 2:
            param = [float(c) for c in self.values.split(',')]
            for i in range(num):
                cond = (param[1] - param[0]) * random.random() + param[0]
                cand.append(cond)
            return cand
