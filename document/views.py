from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from .models import Document, File
from .forms import DocumentForm
from .serializer import DocumentSerializer, FileSerializer
import os
import urllib

class AddView(base.FormView):
    model = Document
    upper = Project
    form_class = DocumentForm
    template_name = "project/default_add.html"
    title = 'Document Add'
    success_name = 'document:list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        file = form.cleaned_data['file']
        note = form.cleaned_data['note']
        comment = form.cleaned_data['comment']
        filename = os.path.basename(file.name)
        title = filename.split('.')[0]
        model = self.model.objects.create(created_by=self.request.user,
                                          updated_by=self.request.user,
                                          upper=upper, title=title, note=note)
        File.objects.create(created_by=self.request.user, upper=model,
                            file=file, comment=comment, edition=0, filename=filename)
        return super().form_valid(form)

class DetailView(base.DetailView):
    model = Document
    template_name = "document/document_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        files = File.objects.filter(upper=model, edition=self.kwargs['ed'])
        if files:
            context['file'] = files[0]
            if files[0].file_ext() == '.zip':
                zipfile_list = files[0].zipfile_list()
                if self.kwargs['zipid'] == 0:
                    context['zipfile_list'] = zipfile_list
                else:
                    zipid = self.kwargs['zipid']
                    if zipid >= 1 and zipid <= len(zipfile_list):
                        context['zipname'] = zipfile_list[zipid - 1]
                    if zipid > 1:
                        context['prev_zipid'] = zipid - 1
                    if zipid <= len(zipfile_list):
                        context['next_zipid'] = zipid + 1
            if self.kwargs['ed'] > 0:
                context['prev_ed'] = self.kwargs['ed'] - 1
            if self.kwargs['ed'] < model.latest_file().edition:
                context['next_ed'] = self.kwargs['ed'] + 1
        return context

class ListView(base.ListView):
    model = Document
    upper = Project
    template_name = "document/document_list.html"
    navigation = [['Add', 'document:add'],
                  ['Import', 'document:import']]

class UpdateView(base.UpdateView):
    model = Document
    fields = ('title', 'status', 'note')
    template_name = "document/document_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        files = File.objects.filter(upper=model).order_by('-edition')
        context['document_files'] = files
        return context

class DeleteView(base.DeleteManagerView):
    model = Document
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Document
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class ContentView(base.View):
    model = Document
    template_name = "document/content.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        files = File.objects.filter(upper=model, edition=self.kwargs['ed'])
        if files:
            if self.kwargs['zipid'] == 0:
                content = files[0].file_content()
            else:
                content = files[0].zipfile_content(self.kwargs['zipid'])
            if 'md' in content or 'texts' in content or 'code' in content or 'plain' in content:
                return render(request, self.template_name, {'content': content})
            elif 'html' in content:
                return HttpResponse(content['html'], content_type='text/html')
            elif 'image' in content:
                response = HttpResponse(content['image'], content_type=content['type'])
                fn = urllib.parse.quote(content['filename'])
                response["Content-Disposition"] = "inline; filename='{0}'; filename*=UTF-8''{1}".format(fn, fn)
                return response
        return HttpResponse('Cannot display content.')

class SearchView(base.SearchView):
    model = Document
    upper = Project
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Document Search'
    session_name = 'document_search'
    back_name = 'document:list'

    def check_child(self, upper, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(comment__icontains=text) |
                  Q(filename__icontains=text), cond)
        file = File.objects.filter(upper=upper).filter(q)
        return file

class FileAddView(base.AddView):
    model = File
    upper = Document
    fields = ('file', 'comment')
    template_name = "project/default_add.html"
    title = 'Upload'
    bdcl_remove = 1

    def form_valid(self, form):
        model = form.save(commit=False)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        files = self.model.objects.filter(upper=upper)
        model.upper = upper
        model.created_by = self.request.user
        if files:
            model.edition = len(files)
        else:
            model.edition = 0
        model.filename = model.file.name
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document:detail',
                       kwargs={'pk': self.object.upper.id, 'ed': self.object.edition})

class FileUpdateView(base.UpdateView):
    model = File
    fields = ('comment',)
    template_name = "project/default_update.html"
    bdcl_remove = 1

class FileView(base.FileView):
    model = File
    attachment = True
    utf8_filename = True

    def get_file(self, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        file = getattr(model, self.field)
        return file, model.filename

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = DocumentSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Document
    serializer_class = DocumentSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Document
    serializer_class = DocumentSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Document
    serializer_class = DocumentSerializer

class FileAddAPIView(base_api.AddAPIView):
    upper = Document
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(created_by=self.request.user, upper=upper)

class FileListAPIView(base_api.ListAPIView):
    upper = Document
    model = File
    serializer_class = FileSerializer

class FileRetrieveAPIView(base_api.RetrieveAPIView):
    model = File
    serializer_class = FileSerializer

class FileFileAPIView(base_api.FileAPIView):
    model = File
    attachment = True

class FileRemote(remote.FileRemote):
    model = File
    add_name = 'document:api_file_add'
    list_name = 'document:api_file_list'
    retrieve_name = 'document:api_file_retrieve'
    file_fields_names = [('file', 'document:api_file_file')]
    serializer_class = FileSerializer

class DocumentRemote(remote.Remote):
    model = Document
    add_name = 'document:api_add'
    list_name = 'document:api_list'
    retrieve_name = 'document:api_retrieve'
    update_name = 'document:api_update'
    serializer_class = DocumentSerializer
    child_remote = [FileRemote]

class ImportView(remote.ImportView):
    model = Document
    upper = Project
    form_class = ImportForm
    remote_class = DocumentRemote
    template_name = "project/default_import.html"
    title = 'Document Import'
    success_name = 'document:list'
    view_name = 'document:detail'

# class CloneView(remote.CloneView):
#     model = Document
#     form_class = CloneForm
#     upper = Project
#     remote_class = DocumentRemote
#     template_name = "project/default_clone.html"
#     title = 'Document Clone'
#     success_name = 'document:list'
#     view_name = 'document:detail'
#
# class TokenView(remote.TokenView):
#     model = Document
#     form_class = TokenForm
#     success_names = ['document:pull', 'document:push']
#
# class PullView(remote.PullView):
#     model = Document
#     remote_class = DocumentRemote
#     success_name = 'document:detail'
#     fail_name = 'document:token'
#
# class PushView(remote.PushView):
#     model = Document
#     remote_class = DocumentRemote
#     success_name = 'document:detail'
#     fail_name = 'document:token'
#
# class SetRemoteView(remote.SetRemoteView):
#     model = Document
#     form_class = SetRemoteForm
#     remote_class = DocumentRemote
#     title = 'Document Set Remote'
#     success_name = 'document:detail'
#     view_name = 'document:detail'
#
# class ClearRemoteView(remote.ClearRemoteView):
#     model = Document
#     remote_class = DocumentRemote
#     success_name = 'document:detail'
