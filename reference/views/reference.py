from django.http import HttpResponse
from django.urls import reverse
from django.template import Template, Context
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from ..models.reference import Reference
from ..models.article import Article, ArticleQueryset
from ..serializer import ReferenceSerializer
from .article import ArticleRemote
from Levenshtein import distance
from pypdf import PdfWriter
from docx import Document
import datetime
import os
import io
import json
import bibtexparser

class AddView(base.AddView):
    model = Reference
    upper = Project
    fields = ('title', 'note', 'order', 'pagesize', 'template', 'startid')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Reference
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:add'],
                  ['Import', 'reference:import'],
                  ['Clone', 'reference:clone'],
                  ['Search', 'reference:search']]

def ArticleSummary(upper):
    articles = Article.objects.filter(upper=upper)
    return {
        'narticles': len(articles)
    }


class DetailView(base.DetailView):
    model = Reference
    template_name = "reference/reference_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        url = reverse('reference:article_list',
                      kwargs={'pk': model.id, 'order': model.order, 'size':model.pagesize})
        nav_list = [base.Link('Article', url)]
        context['navigation_list'] = nav_list
        context['summary'] = ArticleSummary(model)
        if model.data:
            context['model_data'] = json.loads(model.data)
        return context

def RenderText(model):
    try:
        lines = []
        template = Template(model.template)
        for i, art in enumerate(ArticleQueryset(model, model.order)):
            context = Context({
                'id': i + model.startid,
                'type': art.get_type_display(),
                'key': art.key,
                'title': art.title,
                'author': art.author_display(),
                'journal': art.journal,
                'volume': art.volume,
                'number': art.number,
                'month': art.month,
                'year': art.year,
                'pages': art.pages,
                'cited': art.cited,
                'impact': art.impact,
                'booktitle': art.booktitle,
                'publisher': art.publisher,
                'address': art.address,
                'doi': art.doi,
                'url': art.url,
                'filename': art.file.name,
                'abstract': art.abstract,
                'note': art.note
            })
            line = template.render(context)
            line = line.replace('&amp;', '&')
            lines.append([line, art.id])
        return lines
    except:
        return []

def checkSimilar(lines):
    similar = []
    tot = len(lines)
    for i in range(tot):
        for j in range(i+1, tot):
            sim = 1 - distance(lines[i][0], lines[j][0]) / max(len(lines[i][0]), len(lines[j][0]))
            if sim > 0.9:
                similar.append([i, j, sim])
    return similar

class UpdateView(base.UpdateView):
    model = Reference
    fields = ('title', 'status', 'note', 'order', 'pagesize', 'template', 'startid')
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        lines = RenderText(model)
        params = {
            'lines': lines,
            'similar': checkSimilar(lines)
        }
        model.data = json.dumps(params)
        return super().form_valid(form)

class DeleteView(base.DeleteManagerView):
    model = Reference
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Reference
    text_field = "note"
    template_name = "project/default_mdedit.html"

class MergePDFView(base.View):
    model = Reference

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        merger = PdfWriter()
        for art in ArticleQueryset(model, model.order):
            if art.file is not None and os.path.splitext(art.file.name)[-1] == '.pdf':
                with art.file.open('rb') as f:
                    merger.append(f)
        buf = io.BytesIO()
        merger.write(buf)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        buf.close()
        merger.close()
        now = datetime.datetime.now()
        filename = 'MergePDF%s.pdf' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class BibtexView(base.View):
    model = Reference

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        entries = []
        for art in ArticleQueryset(model, model.order):
            entries.append(art.bibentry())
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = entries
        bibstr = bibtexparser.dumps(db)
        response = HttpResponse(bibstr, content_type="text/plain")
        now = datetime.datetime.now()
        filename = 'Reference%s.bib' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class DocxView(base.View):
    model = Reference

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        data = json.loads(model.data)
        document = Document()
        document.add_heading(model.title, 0)
        for line in data['lines']:
            document.add_paragraph(line[0])
        buf = io.BytesIO()
        document.save(buf)
        response = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        buf.close()
        now = datetime.datetime.now()
        filename = 'Reference%s.docx' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

# class DownloadCSVView(base.View):
#     model = Reference
#
#     def get(self, request, **kwargs):
#         model = self.model.objects.get(pk=kwargs['pk'])
#         response = HttpResponse(content_type="text/csv; charset=UTF-8")
#         now = datetime.datetime.now()
#         filename = 'Refefence%s.csv' % (now.strftime('%Y%m%d%H%M%S')[2:])
#         response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
#         writer = csv.writer(response)
#         writer.writerow(['ID', 'Type', 'Title', 'Author', 'Journal', 'Volume', 'Number', 'Year', 'Page', 'Conference', 'Published',
#                         'Cited', 'Impact', 'URL', 'Filename', 'key', 'Note'])
#         for i, art in enumerate(ArticleQueryset(model, model.order)):
#             writer.writerow([i + model.startid, art.get_type_display(), art.title, art.author, art.journal, art.volume, art.number,
#                              art.year, art.page, art.conference, art.published, art.cited, art.impact, art.url, art.file.name,
#                              art.key, art.note])
#         return response

# class UploadCSVView(base.FormView):
#     model = Reference
#     form_class = CSVFileForm
#     template_name = "reference/reference_upload.html"
#     success_name = 'reference:detail'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         model = self.model.objects.get(pk=self.kwargs['pk'])
#         context['title'] = model.title + ' : Upload CSV'
#         context['object'] = model
#         return context
#
#     def form_valid(self, form):
#         model = self.model.objects.get(pk=self.kwargs['pk'])
#         csvfile = io.TextIOWrapper(form.cleaned_data['csv_file'])
#         reader = csv.reader(csvfile)
#         next(reader)
#         for row in reader:
#             try:
#                 ref = Article.objects.get(pk=row[0], upper=model)
#             except:
#                 ref = Article.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=model)
#             updated = False
#             if ref.get_type_word() != row[1]:
#                 ref.set_type_word(row[1])
#                 updated = True
#             if ref.title != row[2]:
#                 ref.title = row[2]
#                 updated = True
#             if ref.author != row[3]:
#                 ref.author = row[3]
#                 updated = True
#             if ref.journal != row[4]:
#                 ref.journal = row[4]
#                 updated = True
#             if ref.volume != row[5]:
#                 ref.volume = row[5]
#                 updated = True
#             if ref.number != row[6]:
#                 ref.number = row[6]
#                 updated = True
#             if ref.year != row[7]:
#                 ref.year = row[7]
#                 updated = True
#             if ref.page != row[8]:
#                 ref.page = row[8]
#                 updated = True
#             if ref.url != row[9]:
#                 ref.url = row[9]
#                 updated = True
#             if ref.note != row[10]:
#                 ref.note = row[10]
#                 updated = True
#             if updated:
#                 ref.save()
#         return super().form_valid(form)

class SearchView(base.SearchView):
    model = Reference
    upper = Project
    form_class = SearchForm
    template_name = "reference/reference_search.html"
    title = 'Reference Search'
    session_name = 'reference_search'
    back_name = 'reference:list'
    lower_items = [{'Search': 'reference.views.article.ArticleSearch'}]

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = ReferenceSerializer

class ListAPIView(base_api.ListAPIView):
    model = Reference
    upper = Project
    serializer_class = ReferenceSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Reference
    serializer_class = ReferenceSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Reference
    serializer_class = ReferenceSerializer

class ReferenceRemote(remote.Remote):
    model = Reference
    add_name = 'reference:api_add'
    list_name = 'reference:api_list'
    retrieve_name = 'reference:api_retrieve'
    update_name = 'reference:api_update'
    serializer_class = ReferenceSerializer
    lower_remote = [ArticleRemote]

class ImportView(remote.ImportView):
    model = Reference
    upper = Project
    form_class = ImportForm
    remote_class = ReferenceRemote
    template_name = "project/default_import.html"
    title = 'Reference Import'
    success_name = 'reference:list'
    view_name = 'reference:detail'
    hidden_lower = False
    default_lower = True

class CloneView(remote.CloneView):
    model = Reference
    form_class = CloneForm
    upper = Project
    remote_class = ReferenceRemote
    template_name = "project/default_clone.html"
    title = 'Reference Clone'
    success_name = 'reference:list'
    view_name = 'reference:detail'

class TokenView(remote.TokenView):
    model = Reference
    form_class = TokenForm
    success_names = ['reference:pull', 'reference:push']

class PullView(remote.PullView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
    fail_name = 'reference:token'

class PushView(remote.PushView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
    fail_name = 'reference:token'

class LogView(remote.LogView):
    model = Reference

class SetRemoteView(remote.SetRemoteView):
    model = Reference
    form_class = SetRemoteForm
    remote_class = ReferenceRemote
    title = 'Reference Set Remote'
    success_name = 'reference:detail'
    view_name = 'reference:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
