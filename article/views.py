from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from diff_match_patch import diff_match_patch
from .models import Article, File, Diff
from .forms import AddForm, UpdateForm, MDFileForm, FileUpdateForm
from .serializer import ArticleSerializer, FileSerializer, DiffSerializer
from io import TextIOWrapper
import datetime

class AddView(base.AddView):
    model = Article
    upper = Project
    form_class = AddForm
    template_name ="article/article_add.html"

class ListView(base.ListView):
    model = Article
    upper = Project
    template_name = "article/article_list.html"
    navigation = [['Add', 'article:add'],
                  ['Import', 'article:import'],
                  ['Clone', 'article:clone'],
                  ['Search', 'article:search']]

class DetailView(base.DetailView):
    model = Article
    template_name = "article/article_detail.html"

def CreateDiff(current, previous, upper, user):
    dmp = diff_match_patch()
    patches = dmp.patch_make(current, previous)
    if len(patches) > 0:
        diff = dmp.patch_toText(patches)
        Diff.objects.create(upper=upper, updated_by=user, diff=diff)

class UpdateView(base.UpdateView):
    model = Article
    form_class = UpdateForm
    template_name = "article/article_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        files = File.objects.filter(upper=model).order_by('-updated_at')
        context['article_files'] = files
        diffs = Diff.objects.filter(upper=model).order_by('-updated_at')
        context['article_diffs'] = diffs
        return context

    def form_valid(self, form):
        curr = form.save(commit=False)
        prev = self.model.objects.get(pk=self.kwargs['pk'])
        CreateDiff(curr.text, prev.text, prev, self.request.user)
        return super().form_valid(form)

class DeleteView(base.DeleteManagerView):
    model = Article
    template_name = "project/default_delete.html"

class UploadView(base.FormView):
    model = Article
    form_class = MDFileForm
    template_name = "project/default_add.html"
    title = 'Article Upload'
    success_name = 'article:detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_title'] = 'Upload'
        return context

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        mdfile = TextIOWrapper(form.cleaned_data['md_file'], encoding='UTF-8')
        previous = model.text
        model.text = mdfile.read()
        model.save()
        CreateDiff(model.text, previous, model, self.request.user)
        return super().form_valid(form)

class DownloadView(base.View):
    model = Article

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        response = HttpResponse(model.text, content_type='text/plain; charset=UTF-8')
        now = datetime.datetime.now()
        filename = 'Article%s.md' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class FileAddView(base.AddView):
    model = File
    upper = Article
    fields = ('title', 'note', 'file')
    template_name = "project/default_add.html"
    bdcl_remove = 1

class FileUpdateView(base.UpdateView):
    model = File
    form_class = FileUpdateForm
    template_name = "project/default_update.html"
    bdcl_remove = 1

class FileDeleteView(base.DeleteView):
    model = File
    template_name = "project/default_delete.html"
    bdcl_remove = 1

class FileFileView(base.FileView):
    model = File
    attachment = False

def PreviousText(model):
    diffs = Diff.objects.filter(upper=model.upper).order_by('-updated_at')
    text = model.upper.text
    dmp = diff_match_patch()
    for diff in diffs:
        patches = dmp.patch_fromText(diff.diff)
        text, _ = dmp.patch_apply(patches, text)
        if diff.id is model.id:
            break
    return text

class DiffPreviousView(base.View):
    model = Diff
    template_name = "article/diff_previous.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'previous_text': PreviousText(model),
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

class DiffDiffView(base.View):
    model = Diff
    template_name = "article/diff_diff.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        previous = PreviousText(model)
        dmp = diff_match_patch()
        diff = dmp.diff_main(previous, model.upper.text)
        pretty = dmp.diff_prettyHtml(diff)
        params = {
            'object': model,
            'pretty': pretty,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

class DiffRestoreView(base.View):
    model = Diff
    template_name = "article/diff_restore.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        previous = model.upper.text
        model.upper.text = PreviousText(model)
        model.upper.save()
        CreateDiff(model.upper.text, previous, model.upper, self.request.user)
        return redirect(model.upper.get_detail_url())

class SearchView(base.SearchView):
    model = Article
    upper = Project
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Article Search'
    session_name = 'article_search'
    back_name = 'article:list'

    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(title__icontains=text) |
                  Q(text__icontains=text), cond)
        return q

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = ArticleSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Article
    serializer_class = ArticleSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Article
    serializer_class = ArticleSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Article
    serializer_class = ArticleSerializer

class FileAddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class FileListAPIView(base_api.ListAPIView):
    upper = Article
    model = File
    serializer_class = FileSerializer

class FileRetrieveAPIView(base_api.RetrieveAPIView):
    model = File
    serializer_class = FileSerializer

class FileUpdateAPIView(base_api.UpdateAPIView):
    model = File
    serializer_class = FileSerializer

class FileDeleteAPIView(base_api.DeleteAPIView):
    model = File
    serializer_class = FileSerializer

class FileFileAPIView(base_api.FileAPIView):
    model = File
    attachment = False

class FileRemote(remote.FileRemote):
    model = File
    add_name = 'article:api_file_add'
    list_name = 'article:api_file_list'
    retrieve_name = 'article:api_file_retrieve'
    update_name = 'article:api_file_update'
    delete_name = 'article:api_file_delete'
    file_fields_names = [('file', 'article:api_file_file')]
    serializer_class = FileSerializer

class DiffAddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = DiffSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class DiffListAPIView(base_api.ListAPIView):
    upper = Article
    model = Diff
    serializer_class = DiffSerializer

class DiffRetrieveAPIView(base_api.RetrieveAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffUpdateAPIView(base_api.UpdateAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffDeleteAPIView(base_api.DeleteAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffRemote(remote.Remote):
    model = Diff
    add_name = 'article:api_diff_add'
    list_name = 'article:api_diff_list'
    retrieve_name = 'article:api_diff_retrieve'
    update_name = 'article:api_diff_update'
    delete_name = 'article:api_diff_delete'
    serializer_class = DiffSerializer
    synchronize = True

class ArticleRemote(remote.Remote):
    model = Article
    add_name = 'article:api_add'
    list_name = 'article:api_list'
    retrieve_name = 'article:api_retrieve'
    update_name = 'article:api_update'
    serializer_class = ArticleSerializer
    child_remote = [FileRemote, DiffRemote]

class ImportView(remote.ImportView):
    model = Article
    upper = Project
    form_class = ImportForm
    remote_class = ArticleRemote
    template_name = "project/default_import.html"
    title = 'Article Import'
    success_name = 'article:list'
    view_name = 'article:detail'

class CloneView(remote.CloneView):
    model = Article
    form_class = CloneForm
    upper = Project
    remote_class = ArticleRemote
    template_name = "project/default_clone.html"
    title = 'Article Clone'
    success_name = 'article:list'
    view_name = 'article:detail'

class TokenView(remote.TokenView):
    model = Article
    form_class = TokenForm
    success_names = ['article:pull', 'article:push']

class PullView(remote.PullView):
    model = Article
    remote_class = ArticleRemote
    success_name = 'article:detail'
    fail_name = 'article:token'

class PushView(remote.PushView):
    model = Article
    remote_class = ArticleRemote
    success_name = 'article:detail'
    fail_name = 'article:token'

class SetRemoteView(remote.SetRemoteView):
    model = Article
    form_class = SetRemoteForm
    remote_class = ArticleRemote
    title = 'Article Set Remote'
    success_name = 'article:detail'
    view_name = 'article:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Article
    remote_class = ArticleRemote
    success_name = 'article:detail'
