from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import HiddenInput
from rest_framework import status
from rest_framework.response import Response
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from diff_match_patch import diff_match_patch
from .models import Article, File, Diff
from .forms import UploadForm, TranslateForm, FileAddForm, FileUpdateForm
from .serializer import ArticleSerializer, PDFSerializer, FileSerializer, DiffSerializer
from .latex import Tex2PDF, GetFile, SVG2PDF
from io import TextIOWrapper, BytesIO
from zipfile import ZipFile
import datetime
import base64
import os
import requests

class AddView(base.AddView):
    model = Article
    upper = Project
    fields = ('title', 'type', 'category', 'public')
    template_name ="article/article_add.html"

class ListView(base.ListView):
    model = Article
    upper = Project
    template_name = "article/article_list.html"
    navigation = [['Add', 'article:add'],
                  ['Import', 'article:import'],
                  ['Search', 'article:search']]

class DetailView(base.DetailView):
    model = Article
    template_name = "article/article_detail.html"

def CreateDiff(current, previous, upper, user, comment=''):
    dmp = diff_match_patch()
    patches = dmp.patch_make(current, previous)
    if len(patches) > 0:
        diff = dmp.patch_toText(patches)
        Diff.objects.create(upper=upper, updated_by=user, diff=diff, comment=comment)

class UpdateView(base.UpdateView):
    model = Article
    fields = ('title', 'status', 'type', 'category', 'public')
    template_name = "article/article_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        diffs = Diff.objects.filter(upper=model).order_by('-updated_at')
        context['article_diffs'] = diffs
        return context

class EditView(base.TemplateView):
    model = Article
    template_name = "article/article_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['object'] = model
        files = File.objects.filter(upper=model)
        context['article_files'] = files
        return context

class DeleteView(base.DeleteManagerView):
    model = Article
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Article
    attachment = False

class UploadView(base.FormView):
    model = Article
    form_class = UploadForm
    template_name = "project/default_add.html"
    title = 'Article Upload'
    success_name = 'article:detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_title'] = 'Upload'
        return context

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        file = TextIOWrapper(form.cleaned_data['file'], encoding='UTF-8')
        previous = model.text
        comment = model.comment
        model.text = file.read()
        model.comment = form.cleaned_data['comment']
        if model.type == 1:
            pdfv, _ = Tex2PDF(model, model.text, self.request)
            if pdfv:
                model.file = InMemoryUploadedFile(ContentFile(pdfv), None, 'ArticleFile.pdf',
                                                  None, len(pdfv), None)
            else:
                model.file = None
        model.save()
        CreateDiff(model.text, previous, model, self.request.user, comment)
        return super().form_valid(form)

class DownloadView(base.View):
    model = Article

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        response = HttpResponse(model.text, content_type='text/plain; charset=UTF-8')
        now = datetime.datetime.now()
        if model.type == 0:
            filename = 'Article%s.md' % (now.strftime('%Y%m%d%H%M%S')[2:])
        elif model.type == 1:
            filename = 'Article%s.tex' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class DownloadZipView(base.View):
    model = Article

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        text = model.text
        files = File.objects.filter(upper=model)
        buf = BytesIO()
        zipf = ZipFile(buf, 'w')
        for file in files:
            if file.svg2pdf:
                name, ext = os.path.splitext(file.name)
                filename = name + '.pdf'
            else:
                filename = file.name
            if file.file:
                content = file.file.read()
            elif file.url:
                content = GetFile(file.url, request)
            if content and file.svg2pdf:
                content = SVG2PDF(content)
            if content:
                zipf.writestr(filename, content)
                if model.type == 0:
                    url = reverse('article:file_file', kwargs={'unique': file.unique})
                    text = text.replace(url, filename)
        if model.type == 0:
            zipf.writestr('main.md', text)
        elif model.type == 1:
            zipf.writestr('main.tex', text)
        zipf.close()
        response = HttpResponse(buf.getvalue(), content_type='application/zip')
        buf.close()
        now = datetime.datetime.now()
        filename = 'Article%s.zip' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class TranslateView(base.FormView):
    model = Article
    form_class = TranslateForm
    template_name = "article/article_add.html"
    title = 'Article Translate'
    success_name = 'article:list'

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = model.title
        return form

    def deepl_api(self, api_key, text, sourcel, targetl, translate):
        if translate == '0':
            url = "https://api-free.deepl.com/v2/translate"
        elif translate == '1':
            url = "https://api.deepl.com/v2/translate"
        params = {
            'auth_key': api_key,
            'text': text,
            'source_lang': sourcel,
            'target_lang': targetl
        }
        request = requests.post(url, data=params)
        if request.status_code == 200:
            result = request.json()
            return result['translations'][0]['text']
        else:
            return text

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        text = self.deepl_api(form.cleaned_data['api_key'], model.text,
                              form.cleaned_data['sourcel'], form.cleaned_data['targetl'],
                              form.cleaned_data['translate'])
        self.model.objects.create(upper=model.upper, status=model.status, type=model.type,
                                  category=model.category, public=model.public, text=text,
                                  title=form.cleaned_data['title'], comment=form.cleaned_data['comment'],
                                  created_by=self.request.user, updated_by=self.request.user)
        return super().form_valid(form)
    def get_success_url(self):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name, kwargs={'pk': model.upper.id})

class FileAddView(base.AddView):
    model = File
    upper = Article
    form_class = FileAddForm
    template_name = "project/default_add.html"
    bdcl_remove = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        if upper.type == 0:
            form.fields['svg2pdf'].widget = HiddenInput()
        return form

class FileListView(base.ListView):
    model = File
    upper = Article
    template_name = "article/file_list.html"
    title = 'Article File'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upper'] = self.upper.objects.get(pk=self.kwargs['pk'])
        context['breadcrumb_list'] = context['breadcrumb_list'][:-1]
        return context

class FileUpdateView(base.UpdateView):
    model = File
    form_class = FileUpdateForm
    template_name = "project/default_update.html"
    bdcl_remove = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.upper.type == 0:
            form.fields['svg2pdf'].widget = HiddenInput()
        return form

class FileDeleteView(base.DeleteView):
    model = File
    template_name = "project/default_delete.html"
    bdcl_remove = 1

class FileFileView(base.FileView):
    model = File
    attachment = False
    use_unique = True

def PreviousText(model):
    diffs = Diff.objects.filter(upper=model.upper).order_by('-updated_at')
    text = model.upper.text
    dmp = diff_match_patch()
    for diff in diffs:
        patches = dmp.patch_fromText(diff.diff)
        text, _ = dmp.patch_apply(patches, text)
        if diff.id == model.id:
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
        comment = model.upper.comment
        model.upper.comment = 'Restore : ' + model.comment
        if model.upper.type == 1:
            pdfv, _, _ = Tex2PDF(model.upper, model.upper.text, self.request)
            if pdfv:
                model.upper.file = InMemoryUploadedFile(ContentFile(pdfv), None, 'ArticleFile.pdf',
                                                        None, len(pdfv), None)
            else:
                model.upper.file = None
        model.upper.save()
        CreateDiff(model.upper.text, previous, model.upper, self.request.user, comment)
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

    def perform_update(self, serializer):
        prev = self.model.objects.get(pk=self.kwargs['pk'])
        instance = serializer.save()
        if instance.type == 1:
            pdfv, _, _ = Tex2PDF(instance, instance.text, self.request)
            if pdfv:
                instance.file = InMemoryUploadedFile(ContentFile(pdfv), None, 'ArticleFile.pdf',
                                                    None, len(pdfv), None)
                instance.save()
            else:
                instance.file = None
        CreateDiff(instance.text, prev.text, prev, self.request.user, prev.comment)

class PDFAPIView(base_api.APIView):
    model = Article
    serializer_class = PDFSerializer

    def post(self, request, *args, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        text = request.data['text']
        if text:
            pdfv, log, std = Tex2PDF(model, text, request)
            if pdfv:
                data = {
                    'type': 'application/pdf',
                    'encode': 'base64',
                    'data': base64.b64encode(pdfv),
                    'log': log
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data = {
                    'type': 'text/plain',
                    'log': log,
                    'std': std
                }
                return Response(data, status=status.HTTP_201_CREATED)
        return Response({}, status=status.HTTP_202_ACCEPTED)

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

# class CloneView(remote.CloneView):
#     model = Article
#     form_class = CloneForm
#     upper = Project
#     remote_class = ArticleRemote
#     template_name = "project/default_clone.html"
#     title = 'Article Clone'
#     success_name = 'article:list'
#     view_name = 'article:detail'
#
# class TokenView(remote.TokenView):
#     model = Article
#     form_class = TokenForm
#     success_names = ['article:pull', 'article:push']
#
# class PullView(remote.PullView):
#     model = Article
#     remote_class = ArticleRemote
#     success_name = 'article:detail'
#     fail_name = 'article:token'
#
# class PushView(remote.PushView):
#     model = Article
#     remote_class = ArticleRemote
#     success_name = 'article:detail'
#     fail_name = 'article:token'
#
# class SetRemoteView(remote.SetRemoteView):
#     model = Article
#     form_class = SetRemoteForm
#     remote_class = ArticleRemote
#     title = 'Article Set Remote'
#     success_name = 'article:detail'
#     view_name = 'article:detail'
#
# class ClearRemoteView(remote.ClearRemoteView):
#     model = Article
#     remote_class = ArticleRemote
#     success_name = 'article:detail'
