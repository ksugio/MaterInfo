from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo
from .reference import Reference
import os
import bibtexparser

def ReferenceUploadTo(instance, filename):
    return filename

class Article(Created, Updated, Remote):
    upper = models.ForeignKey(Reference, verbose_name='Reference', on_delete=models.CASCADE)
    TypeChoices = ((0, 'Article'), (1, 'Book'), (2, 'Booklet'), (3, 'InBook'), (4, 'InCollection'),
                   (5, 'InProceedings'), (6, 'Manual'), (7, 'MastersThesis'),  (8, 'Misc'), (9, 'PhdThesis'),
                   (10, 'Proceedings'),  (11, 'TechReport'), (12, 'Unpublished'))
    type = models.PositiveSmallIntegerField(verbose_name='Type', choices=TypeChoices, default=0)
    key = models.CharField(verbose_name='Key', max_length=20, blank=True)
    title = models.TextField(verbose_name='Title')
    author = models.TextField(verbose_name='Author', blank=True)
    journal = models.CharField(verbose_name='Journal', max_length=100, blank=True)
    volume = models.CharField(verbose_name='Volume', max_length=10, blank=True)
    number = models.CharField(verbose_name='Number', max_length=10, blank=True)
    month = models.CharField(verbose_name='Month', max_length=20, blank=True)
    year = models.CharField(verbose_name='Year', max_length=10, blank=True)
    pages = models.CharField(verbose_name='Pages', max_length=20, blank=True)
    cited = models.PositiveIntegerField(verbose_name='Times cited', blank=True, null=True)
    impact = models.FloatField(verbose_name='Impact factor', blank=True, null=True)
    booktitle = models.TextField(verbose_name='Book Title', blank=True)
    publisher = models.CharField(verbose_name='Publisher', max_length=100, blank=True)
    address = models.CharField(verbose_name='Address', max_length=100, blank=True)
    doi = models.CharField(verbose_name='DOI', max_length=200, blank=True)
    url = models.URLField(verbose_name='URL', max_length=200, blank=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)
    abstract = models.TextField(verbose_name='Abstract', blank=True)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:article_list', kwargs={'pk': self.upper.id, 'order': self.upper.order, 'size':self.upper.pagesize})

    def get_detail_url(self):
        return reverse('reference:article_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:article_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:article_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_article_update', kwargs={'pk': self.id})

    def basename(self):
        return os.path.basename(self.file.name)

    def set_type_word(self, word):
        for item in self.TypeChoices:
            if item[1] == word:
                self.type = item[0]
                return
        self.type = self.TypeChoices[-1][0]

    def author_display(self):
        names = self.author.split(' and ')
        return ', '.join(names)

    def bibentry(self):
        entry = {}
        if self.type == 0:
            entry['ENTRYTYPE'] = 'article'
        elif self.type == 1:
            entry['ENTRYTYPE'] = 'book'
        elif self.type == 2:
            entry['ENTRYTYPE'] = 'booklet'
        elif self.type == 3:
            entry['ENTRYTYPE'] = 'inbook'
        elif self.type == 4:
            entry['ENTRYTYPE'] = 'incollection'
        elif self.type == 5:
            entry['ENTRYTYPE'] = 'inproceedings'
        elif self.type == 6:
            entry['ENTRYTYPE'] = 'manual'
        elif self.type == 7:
            entry['ENTRYTYPE'] = 'mastersthesis'
        elif self.type == 8:
            entry['ENTRYTYPE'] = 'misc'
        elif self.type == 9:
            entry['ENTRYTYPE'] = 'phdthesis'
        elif self.type == 10:
            entry['ENTRYTYPE'] = 'proceedings'
        elif self.type == 11:
            entry['ENTRYTYPE'] = 'techreport'
        elif self.type == 12:
            entry['ENTRYTYPE'] = 'unpublished'
        if self.key:
            entry['ID'] = self.key
        else:
            entry['ID'] = 'Article%d' % self.id
        if self.title:
            entry['title'] = self.title
        if self.author:
            entry['author'] = self.author
        if self.journal:
            entry['journal'] = self.journal
        if self.volume:
            entry['volume'] = self.volume
        if self.number:
            entry['number'] = self.number
        if self.month:
            entry['month'] = self.month
        if self.year:
            entry['year'] = self.year
        if self.pages:
            entry['pages'] = self.pages
        if self.booktitle:
            entry['booktitle'] = self.booktitle
        if self.publisher:
            entry['publisher'] = self.publisher
        if self.address:
            entry['address'] = self.address
        if self.doi:
            entry['doi'] = self.doi
        if self.url:
            entry['url'] = self.url
        if self.abstract:
            entry['abstract'] = self.abstract
        if self.note:
            entry['note'] = self.note
        return entry

def ArticleQueryset(upper, order):
    if order == 0:
        return Article.objects.filter(upper=upper).order_by('-created_at')
    elif order == 1:
        return Article.objects.filter(upper=upper).order_by('created_at')
    elif order == 2:
        return Article.objects.filter(upper=upper).order_by('-updated_at')
    elif order == 3:
        return Article.objects.filter(upper=upper).order_by('updated_at')
    elif order == 4:
        return Article.objects.filter(upper=upper).order_by('-year', '-updated_at')
    elif order == 5:
        return Article.objects.filter(upper=upper).order_by('year', 'updated_at')
    elif order == 6:
        return Article.objects.filter(upper=upper).order_by('key')
    elif order == 7:
        return Article.objects.filter(upper=upper).order_by('-key')
    else:
        return Article.objects.filter(upper=upper)
