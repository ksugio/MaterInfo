from django.http import HttpResponse
from django.db.models import Q
from project.views import base, base_api, remote
from project.forms import CSVFileForm, EditNoteForm, ImportForm, SearchForm
from ..models import Reference, Article
from ..forms import ArticleUpdateForm
from ..serializer import ArticleSerializer
import datetime
import io
import csv

class AddView(base.AddView):
    model = Article
    upper = Reference
    fields = ('title', 'author', 'journal', 'volume', 'year', 'page', 'url', 'file', 'type', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Article
    upper = Reference
    template_name = "reference/article_list.html"
    navigation = [['Add', 'reference:article_add'],
                  ['Import', 'reference:article_import'],
                  ['Upload', 'reference:article_upload'],
                  ['Download', 'reference:article_download']]
    paginate_by = 12

class DetailView(base.DetailView):
    model = Article
    template_name = "reference/article_detail.html"
    navigation = []

class UpdateView(base.UpdateView):
    model = Article
    form_class = ArticleUpdateForm
    template_name = "project/default_update.html"

class EditNoteView(base.EditNoteView):
    model = Article
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Article
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Article
    attachment = False

class UploadView(base.FormView):
    model = Article
    upper = Reference
    form_class = CSVFileForm
    template_name = "project/default_add.html"
    title = 'Article Upload'
    success_name = 'reference:article_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_title'] = 'Upload'
        return context

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        csvfile = io.TextIOWrapper(form.cleaned_data['csv_file'])
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            try:
                ref = self.model.objects.get(pk=row[0], upper=upper)
            except:
                ref = self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper)
            updated = False
            if ref.get_type_word() != row[1]:
                ref.set_type_word(row[1])
                updated = True
            if ref.title != row[2]:
                ref.title = row[2]
                updated = True
            if ref.author != row[3]:
                ref.author = row[3]
                updated = True
            if ref.journal != row[4]:
                ref.journal = row[4]
                updated = True
            if ref.volume != row[5]:
                ref.volume = row[5]
                updated = True
            if ref.year != row[6]:
                ref.year = row[6]
                updated = True
            if ref.page != row[7]:
                ref.page = row[7]
                updated = True
            if ref.url != row[8]:
                ref.url = row[8]
                updated = True
            if ref.note != row[9]:
                ref.note = row[9]
                updated = True
            if updated:
                ref.save()
        return super().form_valid(form)

class DownloadView(base.View):
    upper = Reference

    def get(self, request, **kwargs):
        upper = self.upper.objects.get(pk=kwargs['pk'])
        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        now = datetime.datetime.now()
        filename = 'Article%s.csv' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        writer = csv.writer(response)
        writer.writerow(['ID', 'Type', 'Title', 'Author', 'Journal', 'Volume', 'Year', 'Page', 'URL', 'Note', 'File'])
        for art in Article.objects.filter(upper=upper):
            writer.writerow([art.pk, art.get_type_word(), art.title, art.author, art.journal, art.volume, art.year, art.page,
                            art.url, art.note, art.file])
        return response

class ArticleSearch(base.Search):
    model = Article

    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(title__icontains=text) |
                  Q(author__icontains=text) |
                  Q(journal__icontains=text) |
                  Q(volume__icontains=text) |
                  Q(year__icontains=text) |
                  Q(page__icontains=text) |
                  Q(url__icontains=text) |
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

class ImportView(remote.ImportView):
    model = Article
    upper = Reference
    form_class = ImportForm
    remote_class = ArticleRemote
    template_name = "project/default_import.html"
    title = 'Article Import'
    success_name = 'reference:article_list'
    view_name = 'reference:article_detail'
