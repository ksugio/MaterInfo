from django.db import models
from django.urls import reverse
from project.models import Created, Updated, RemoteRoot, Remote, Project, ModelUploadTo
import os

def ReferenceUploadTo(instance, filename):
    return filename

class Reference(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:delete', kwargs={'pk': self.id})

class Article(Created, Updated, Remote):
    upper = models.ForeignKey(Reference, verbose_name='Reference', on_delete=models.CASCADE)
    title = models.TextField(verbose_name='Title')
    author = models.TextField(verbose_name='Author', blank=True)
    journal = models.CharField(verbose_name='Journal', max_length=100, blank=True)
    volume = models.CharField(verbose_name='Volume', max_length=10, blank=True)
    year = models.CharField(verbose_name='Year', max_length=10, blank=True)
    page = models.CharField(verbose_name='Page', max_length=20, blank=True)
    url = models.URLField(verbose_name='URL', max_length=200, blank=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)
    TypeChoices = ((0, 'Paper'), (1, 'Proceeding'), (2, 'Abstract'), (3, 'Book'), (4, 'Thesis'), (5, 'Other'))
    type = models.PositiveSmallIntegerField(verbose_name='Type', choices=TypeChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:article_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:article_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:article_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:article_delete', kwargs={'pk': self.id})

    def basename(self):
        return os.path.basename(self.file.name)

    def get_type_word(self):
        for item in self.TypeChoices:
            if item[0] == self.type:
                return item[1]

    def set_type_word(self, word):
        for item in self.TypeChoices:
            if item[1] == word:
                self.type = item[0]
                return
        self.type = self.TypeChoices[-1][0]
