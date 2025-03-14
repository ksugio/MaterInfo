from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from sample.models import Sample

class General(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    CategoryChoices = ((0, 'process'), (1, 'structure'), (2, 'property'), (3, 'performance'))
    category = models.PositiveSmallIntegerField(verbose_name='Category', choices=CategoryChoices, default=0)
    value = models.FloatField(verbose_name='Value')

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('general:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('general:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('general:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('general:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('general:api_update', kwargs={'pk': self.id})

    def feature(self):
        if self.status or self.upper.status:
            return {}
        else:
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': self.get_category_display(),
                prefix: self.value
            }
