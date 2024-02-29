from django.db import models
from django.urls import reverse
from project.models import Project, Created, Updated, Remote, RemoteRoot, UpperModelUploadTo
import os

def DocumentUploadTo(instance, filename):
    return filename

class Document(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Active'), (1, 'Stop'), (2, 'Finish'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('document:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('document:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('document:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('document:delete', kwargs={'pk': self.id})

    def latest_file(self):
        files = File.objects.filter(upper=self).order_by('-edition')
        if files:
            return files[0]
        else:
            return None

class File(Created, Remote):
    upper = models.ForeignKey(Document, verbose_name='Document', on_delete=models.CASCADE)
    file = models.FileField(verbose_name='File', upload_to=UpperModelUploadTo)
    comment = models.TextField(verbose_name='Comment', blank=True)
    edition = models.PositiveSmallIntegerField(verbose_name='Edition')
    filename = models.CharField(verbose_name='Filename', max_length=256)

    def get_detail_url(self):
        return reverse('document:detail', kwargs={'pk': self.upper.id})

    def basename(self):
        return os.path.basename(self.file.name)

    def title(self):
        return '{} : Edition {} Comment'.format(self.upper.title, self.edition)

