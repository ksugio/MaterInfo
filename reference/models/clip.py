from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo
from .article import Article
from pypdf import PdfReader, PdfWriter
from io import BytesIO

class Clip(Created, Updated, Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    start = models.PositiveSmallIntegerField(verbose_name='Start Page', blank=True, null=True)
    end = models.PositiveSmallIntegerField(verbose_name='End Page', blank=True, null=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:clip_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:clip_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:clip_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:clip_delete', kwargs={'pk': self.id})

    def check_page(self, page):
        if self.start and page < self.start:
            return False
        elif self.end and page > self.end:
            return False
        else:
            return True

    def clip_pdf(self):
        writer = PdfWriter()
        with self.upper.file.open('rb') as f:
            reader = PdfReader(f)
            for i in range(len(reader.pages)):
                if self.check_page(i + 1):
                    writer.add_page(reader.pages[i])
        buf = BytesIO()
        writer.write(buf)
        self.file.save('Clip.pdf', buf, save=False)
        buf.close()
