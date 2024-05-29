from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from config.settings import IMAGE_LOWER
from project.views import base, base_api, remote
from project.forms import EditNoteForm, ImportForm, SearchForm
from project.models import FileSearch
from sample.models import Sample
from ..models.image import Image
from ..models.filter import Filter
from ..serializer import ImageSerializer
from ..forms import ImageAddForm, ImageUpdateForm, ImageGetForm
import os
import datetime
import zipfile
import requests

class AddView(base.FormView):
    model = Image
    upper = Sample
    form_class = ImageAddForm
    template_name ="project/default_add.html"
    title = 'Image Add'
    success_name = 'image:list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        note = form.cleaned_data['note']
        files = form.files.getlist('file')
        scale = form.cleaned_data['scale']
        scaleunit = form.cleaned_data['scaleunit']
        scalepixels = form.cleaned_data['scalepixels']
        device = form.cleaned_data['device']
        for file in files:
            title = os.path.splitext(os.path.basename(file.name))[0]
            self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                title=title, note=note, file=file, scale=scale, scaleunit=scaleunit, scalepixels=scalepixels, device=device)
        return super().form_valid(form)

class GetView(base.FormView, FileSearch):
    model = Image
    upper = Sample
    form_class = ImageGetForm
    template_name = "project/default_add.html"
    title = 'Image Get'
    success_name = 'image:list'

    def get_file(self, url):
        if url.startswith('http'):
            response = requests.get(url)
            if response.status_code != 200:
                return None
            else:
                data = response.content
                ctype = response.headers['Content-Type']
                if ctype == 'image/jpeg':
                    fname = 'Image.jpg'
                elif ctype == 'image/png':
                    fname = 'Image.png'
                elif ctype == 'image/bmp':
                    fname = 'Image.bmp'
                elif ctype == 'image/tiff':
                    fname = 'Image.tif'
                else:
                    return None
        else:
            file = self.file_search(url)
            if file is None:
                return None
            else:
                with file.open('rb') as f:
                    data = f.read()
                fname = os.path.basename(file.name)
        return InMemoryUploadedFile(ContentFile(data), None, fname,
                                    None, len(data), None)

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        url = form.cleaned_data['url']
        title = form.cleaned_data['title']
        note = form.cleaned_data['note']
        scale = form.cleaned_data['scale']
        scaleunit = form.cleaned_data['scaleunit']
        scalepixels = form.cleaned_data['scalepixels']
        device = form.cleaned_data['device']
        file = self.get_file(url)
        if file:
            self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                                      title=title, note=note, file=file, scale=scale, scaleunit=scaleunit,
                                      scalepixels=scalepixels, device=device)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Image
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:add'],
                  ['Get', 'image:get'],
                  ['Import', 'image:import'],
                  ['Download', 'image:download'],
                  ['Search', 'image:search']]

class DetailView(base.DetailView):
    model = Image
    template_name = "image/image_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in IMAGE_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        return super().get_context_data(**kwargs)

class UpdateView(base.UpdateView):
    model = Image
    form_class = ImageUpdateForm
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Image
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = Image
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class FileView(base.FileView):
    model = Image
    attachment = False
    use_unique = True

class DownloadView(base.View):
    upper = Sample

    def get(self, request, **kwargs):
        sample = self.upper.objects.get(pk=kwargs['pk'])
        images = Image.objects.filter(upper=sample)
        response = HttpResponse(content_type='application/zip')
        zipf = zipfile.ZipFile(response, 'w')
        for image in images:
            basename = os.path.basename(image.file.name)
            zipf.writestr(basename, image.file.read())
        now = datetime.datetime.now()
        filename = 'Images_%s.zip' % (now.strftime('%Y%m%d_%H%M%S'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response

class SearchView(base.SearchView):
    model = Image
    upper = Sample
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Image Search'
    session_name = 'image_search'
    back_name = "image:list"
    lower_items = IMAGE_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = ImageSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = Image
    serializer_class = ImageSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Image
    serializer_class = ImageSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Image
    serializer_class = ImageSerializer

class FileAPIView(base_api.FileAPIView):
    model = Image

class ImageRemote(remote.FileRemote):
    model = Image
    add_name = 'image:api_add'
    list_name = 'image:api_list'
    retrieve_name = 'image:api_retrieve'
    update_name = 'image:api_update'
    file_fields_names = [('file', 'image:api_file')]
    serializer_class = ImageSerializer
    lower_items = IMAGE_LOWER

class ImportView(remote.ImportView):
    model = Image
    upper = Sample
    form_class = ImportForm
    remote_class = ImageRemote
    template_name = "project/default_import.html"
    title = 'Image Import'
    success_name = 'image:list'
    view_name = 'image:detail'
    hidden_lower = False
    default_lower = False
