from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from project.models import Created, Updated, Remote, Project, ModelUploadTo, UpperModelUploadTo, Unique

def ArticleUploadTo(instance, filename):
    return filename

class Article(Created, Updated, Remote):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Writing'), (1, 'Reviewing'), (2, 'Revising'), (3, 'Finish'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    TypeChoices = ((0, 'Markdown'), (1, 'LaTex'))
    type = models.PositiveSmallIntegerField(verbose_name='Type', choices=TypeChoices, default=0)
    CategoryChoices = ((0, 'Misc'), (1, 'Report'), (2, 'Thesis'), (3, 'Paper'), (4, 'Conference'), (5, 'Event'), (6, 'Manual'), (7, 'Information'))
    category = models.PositiveSmallIntegerField(verbose_name='Category', choices=CategoryChoices, default=0)
    public = models.BooleanField(verbose_name='Public', default=False)
    text = models.TextField(verbose_name='Text', blank=True)
    comment = models.TextField(verbose_name='Comment', blank=True)
    file = models.FileField(verbose_name='PDF file', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('article:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('article:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('article:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('article:delete', kwargs={'pk': self.id})

    def get_public_url(self):
        return reverse('article:public_detail', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('article:api_update', kwargs={'pk': self.id})

    def get_apipdf_url(self):
        return reverse('article:api_pdf', kwargs={'pk': self.id})

class File(Updated, Remote, Unique):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_upper")
    name = models.CharField(verbose_name='Name', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.FileField(verbose_name='File', upload_to=UpperModelUploadTo, blank=True, null=True)
    url = models.CharField(verbose_name='URL', max_length=256, blank=True)
    svg2pdf = models.BooleanField(verbose_name='SVG to PDF', default=False)

    def get_list_url(self):
        return reverse('article:file_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('article:file_list', kwargs={'pk': self.upper.id})

class Diff(Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    diff = models.TextField(verbose_name='Diff')
    comment = models.TextField(verbose_name='Comment', blank=True)
    updated_by = models.ForeignKey(CustomUser, verbose_name='Updated by', on_delete=models.PROTECT)
    updated_at = models.DateTimeField(verbose_name='Updated at', default=timezone.now)
