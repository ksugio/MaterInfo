from django.utils.module_loading import import_string
from django.http import HttpResponse
from django.urls import reverse
from project.views import base, base_api, remote
from project.models import Project
from project.forms import EditNoteForm
from ..models.album import Album
from ..models.item import Item
from .item import ItemRemote
from ..serializer import AlbumSerializer
import urllib

class AddView(base.AddView):
    model = Album
    upper = Project
    fields = ('title', 'note', 'ncol', 'margin', 'bgcolor', 'format')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Alb' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.saveimg()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Album
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'album:add']]

class DetailView(base.DetailView):
    model = Album
    template_name = "album/album_detail.html"
    navigation = []

class UpdateView(base.UpdateView):
    model = Album
    fields = ('title', 'status', 'note', 'ncol', 'margin', 'bgcolor', 'format')
    template_name = "album/album_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        items = Item.objects.filter(upper=model).order_by('order')
        item_detail = []
        for item in items:
            detail_url = '/'.join(item.url.split('/')[:-1])
            item_detail.append((item, detail_url))
        context['item_detail'] = item_detail
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        prev = model.file.url
        model.saveimg()
        response = super().form_valid(form)
        items = Item.objects.filter(url=prev)
        for item in items:
            item.url = model.file.url
            item.save()
        return response

class EditNoteView(base.EditNoteView):
    model = Album
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Album
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Album
    attachment = False

class AlbumSearch(base.Search):
    model = Album

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = AlbumSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Album
    serializer_class = AlbumSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Album
    serializer_class = AlbumSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Album
    serializer_class = AlbumSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Album
    serializer_class = AlbumSerializer

class FileAPIView(base_api.FileAPIView):
    model = Album
    attachment = False

class AlbumRemote(remote.FileRemote):
    model = Album
    add_name = 'album:api_add'
    list_name = 'album:api_list'
    retrieve_name = 'album:api_retrieve'
    update_name = 'album:api_update'
    delete_name = 'album:api_delete'
    file_fields_names = [('file', 'album:api_file')]
    serializer_class = AlbumSerializer
    child_remote = [ItemRemote]

# class ImportView(remote.ImportView):
#     model = Album
#     upper = Project
#     form_class = ImportForm
#     remote_class = AlbumRemote
#     template_name = "project/default_import.html"
#     title = 'Album Import'
#     success_name = 'album:list'
#     view_name = 'album:detail'
