from django.http import HttpResponse
from django.db.models import Q
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from project.views import base, base_api, remote
from project.forms import ImportForm
from ..models.reference import Reference
from ..models.article import Article, ArticleQueryset
from ..forms import DOIForm, BibtexForm, ZipForm, ArticleUpdateForm
from ..serializer import ArticleSerializer
from .text import TextRemote
from .image import ImageRemote
from .clip import ClipRemote
from crossref.restful import Works
from zipfile import ZipFile
import datetime
import bibtexparser
import json

class AddView(base.AddView):
    model = Article
    upper = Reference
    fields = ('type', 'key', 'title', 'author', 'journal', 'volume', 'number',
              'month', 'year', 'pages', 'cited', 'impact', 'booktitle',
              'publisher', 'address', 'doi', 'url', 'file', 'abstract', 'note')
    template_name ="project/default_add.html"

class DOIView(base.FormView):
    model = Article
    upper = Reference
    form_class = DOIForm
    template_name = "project/default_add.html"
    title = 'DOI Add'
    success_name = 'reference:article_list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        entry = Works().doi(form.cleaned_data['doi'])
        param = {}
        if 'type' in entry:
            if entry['type'] == 'journal-article':
                param['type'] = 0
        key = ''
        if 'title' in entry:
            param['title'] = entry['title'][0]
        if 'author' in entry:
            author = ''
            for auth in entry['author']:
                if 'given' in auth and 'family' in auth:
                    author += '%s %s and ' % (auth['given'], auth['family'])
                    if 'sequence' in auth and auth['sequence'] == 'first':
                        key = auth['family']
            if author:
                param['author'] = author[:-5]
        if 'container-title' in entry:
            param['journal'] = entry['container-title'][0]
        if 'volume' in entry:
            param['volume'] = entry['volume']
        if 'issue' in entry:
            param['number'] = entry['issue']
        if 'issued' in entry:
            if 'date-parts' in entry['issued']:
                dateparts = entry['issued']['date-parts']
                param['year'] = str(dateparts[0][0])
                if key:
                    key += param['year']
                if len(dateparts[0]) >= 2:
                    param['month'] = str(dateparts[0][1])
                    if key:
                        key += '%02d' % (dateparts[0][1])
        if 'page' in entry:
            param['pages'] = entry['page']
        if 'publisher' in entry:
            param['publisher'] = entry['publisher']
        if 'DOI' in entry:
            param['doi'] = entry['DOI']
        if 'URL' in entry:
            param['url'] = entry['URL']
        if 'abstract' in entry:
            param['abstract'] = entry['abstract']
        if key:
            param['key'] = key
        if 'title' in param:
            self.model.objects.create(created_by=self.request.user, updated_by=self.request.user,
                                      upper=upper, **param)
        return super().form_valid(form)

    def get_success_url(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name,
                       kwargs={'pk': self.kwargs['pk'], 'order': upper.order, 'size': upper.pagesize})

class BibtexView(base.FormView):
    model = Article
    upper = Reference
    form_class = BibtexForm
    template_name = "project/default_add.html"
    title = 'Bibtex Add'
    success_name = 'reference:article_list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        bib = bibtexparser.load(form.cleaned_data['file'])
        for entry in bib.entries:
            param = {}
            if 'ENTRYTYPE' in entry:
                type = entry['ENTRYTYPE']
                if type == 'article':
                    param['type'] = 0
                elif type == 'book':
                    param['type'] = 1
                elif type == 'booklet':
                    param['type'] = 2
                elif type == 'inbook':
                    param['type'] = 3
                elif type == 'incollection':
                    param['type'] = 4
                elif type == 'inproceedings':
                    param['type'] = 5
                elif type == 'manual':
                    param['type'] = 6
                elif type == 'mastersthesis':
                    param['type'] = 7
                elif type == 'misc':
                    param['type'] = 8
                elif type == 'phdthesis':
                    param['type'] = 9
                elif type == 'proceedings':
                    param['type'] = 10
                elif type == 'techreport':
                    param['type'] = 11
                elif type == 'unpublished':
                    param['type'] = 12
            if 'ID' in entry:
                param['key'] = entry['ID']
            if 'title' in entry:
                param['title'] = entry['title']
            if 'author' in entry:
                param['author'] = entry['author']
            if 'journal' in entry:
                param['journal'] = entry['journal']
            if 'volume' in entry:
                param['volume'] = entry['volume']
            if 'number' in entry:
                param['number'] = entry['number']
            if 'month' in entry:
                param['month'] = entry['month']
            if 'year' in entry:
                param['year'] = entry['year']
            if 'pages' in entry:
                param['pages'] = entry['pages']
            if 'booktitle' in entry:
                param['booktitle'] = entry['booktitle']
            if 'publisher' in entry:
                param['publisher'] = entry['publisher']
            if 'address' in entry:
                param['address'] = entry['address']
            if 'doi' in entry:
                param['doi'] = entry['doi']
            if 'url' in entry:
                param['url'] = entry['url']
            if 'abstract' in entry:
                param['abstract'] = entry['abstract']
            if 'note' in entry:
                param['note'] = entry['note']
            if 'title' in param:
                self.model.objects.create(created_by=self.request.user, updated_by=self.request.user,
                                          upper=upper, **param)
        return super().form_valid(form)

    def get_success_url(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name,
                       kwargs={'pk': self.kwargs['pk'], 'order': upper.order, 'size': upper.pagesize})

class ZipView(base.FormView):
    model = Article
    upper = Reference
    form_class = ZipForm
    template_name = "project/default_add.html"
    title = 'Zip Add'
    success_name = 'reference:article_list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        with ZipFile(form.cleaned_data['file'], 'r') as zip:
            namelist = zip.namelist()
            if 'reference.json' in namelist:
                with zip.open('reference.json', 'r') as fp:
                    content = fp.read().decode('utf-8')
                    data = json.loads(content)
                for dat in data:
                    filename = dat.pop('filename')
                    if filename in namelist:
                        with zip.open(filename, 'r') as fp:
                            file_content = fp.read()
                        dat['file'] = InMemoryUploadedFile(ContentFile(file_content), None, filename,
                                                           None, len(file_content), None)
                    self.model.objects.create(created_by=self.request.user, updated_by=self.request.user,
                                              upper=upper, **dat)
        return super().form_valid(form)

    def get_success_url(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name,
                       kwargs={'pk': self.kwargs['pk'], 'order': upper.order, 'size': upper.pagesize})

class ListView(base.ListView):
    model = Article
    upper = Reference
    template_name = "reference/article_list.html"
    navigation = [['Add', 'reference:article_add'],
                  ['DOI', 'reference:article_doi'],
                  ['BibTex', 'reference:article_bibtex'],
                  ['Zip', 'reference:article_zip'],
                  ['Import', 'reference:article_import']]
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        context['startid'] = upper.startid
        return context

    def get_queryset(self):
        if self.kwargs['size'] == 0:
            self.paginate_by = 10
        elif self.kwargs['size'] == 1:
            self.paginate_by = 20
        elif self.kwargs['size'] == 2:
            self.paginate_by = 50
        elif self.kwargs['size'] == 3:
            self.paginate_by = 100
        elif self.kwargs['size'] == 4:
            self.paginate_by = 200
        elif self.kwargs['size'] == 5:
            self.paginate_by = 500
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return ArticleQueryset(upper, self.kwargs['order'])

class DetailView(base.DetailView):
    model = Article
    template_name = "reference/article_detail.html"
    navigation = [['Text', 'reference:text_list'],
                  ['Image', 'reference:image_list'],
                  ['Clip', 'reference:clip_list']]

class UpdateView(base.UpdateView):
    model = Article
    form_class = ArticleUpdateForm
    template_name = "project/default_update.html"

class EditNoteView(base.MDEditView):
    model = Article
    text_field = "note"
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Article
    template_name = "project/default_delete.html"

class MoveView(base.MoveView):
    model = Article
    template_name = "project/default_update.html"

class FileView(base.FileView):
    model = Article
    attachment = False

class GetBibtexView(base.View):
    model = Article

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [model.bibentry()]
        bibstr = bibtexparser.dumps(db)
        response = HttpResponse(bibstr, content_type="text/plain")
        now = datetime.datetime.now()
        filename = 'Article%s.bib' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class ArticleSearch(base.Search):
    model = Article
    lower_items = [{'Search': 'reference.views.text.TextSearch'},
                   {'Search': 'reference.views.image.ImageSearch'},
                   {'Search': 'reference.views.clip.ClipSearch'}]

    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(key__icontains=text) |
                  Q(title__icontains=text) |
                  Q(author__icontains=text) |
                  Q(journal__icontains=text) |
                  Q(volume__icontains=text) |
                  Q(number__icontains=text) |
                  Q(month__icontains=text) |
                  Q(year__icontains=text) |
                  Q(pages__icontains=text) |
                  Q(booktitle__icontains=text) |
                  Q(publisher__icontains=text) |
                  Q(address__icontains=text) |
                  Q(doi__icontains=text) |
                  Q(url__icontains=text) |
                  Q(abstract__icontains=text) |
                  Q(note__icontains=text), cond)
        return q

# API
class AddAPIView(base_api.AddAPIView):
    upper = Reference
    serializer_class = ArticleSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Reference
    model = Article
    serializer_class = ArticleSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Article
    serializer_class = ArticleSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Article
    serializer_class = ArticleSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Article
    serializer_class = ArticleSerializer

class FileAPIView(base_api.FileAPIView):
    model = Article
    attachment = False

class ArticleRemote(remote.FileRemote):
    model = Article
    add_name = 'reference:api_article_add'
    list_name = 'reference:api_article_list'
    retrieve_name = 'reference:api_article_retrieve'
    update_name = 'reference:api_article_update'
    delete_name = 'reference:api_article_delete'
    file_fields_names = [('file', 'reference:api_article_file')]
    serializer_class = ArticleSerializer
    lower_remote = [TextRemote, ImageRemote, ClipRemote]

class ImportView(remote.ImportView):
    model = Article
    upper = Reference
    form_class = ImportForm
    remote_class = ArticleRemote
    template_name = "project/default_import.html"
    title = 'Article Import'
    success_name = 'reference:article_list'
    view_name = 'reference:article_detail'
    hidden_lower = False
    default_lower = True