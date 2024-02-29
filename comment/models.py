from django.db import models
from django.urls import reverse
from project.models import Project, Created, Remote, ModelUploadTo
import os

def CommentUploadTo(instance, filename):
    return filename

class Comment(Created, Remote):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=200)
    comment = models.TextField(verbose_name='Comment')
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('comment:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('comment:detail', kwargs={'pk': self.id})

    def basename(self):
        return os.path.basename(self.file.name)

class Response(Created, Remote):
    upper = models.ForeignKey(Comment, verbose_name='Comment', on_delete=models.CASCADE)
    response = models.TextField(verbose_name='Response')
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)

    def __str__(self):
        return self.response

    def get_list_url(self):
        return reverse('comment:list', kwargs={'pk': self.upper.upper.id})

    def get_detail_url(self):
        return reverse('comment:list', kwargs={'pk': self.upper.upper.id})

    def basename(self):
        return os.path.basename(self.file.name)
