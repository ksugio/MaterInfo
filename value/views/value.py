from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from config.settings import VALUE_LOWER
from django.shortcuts import render
from project.views import base, base_api, remote
from project.forms import EditNoteForm, ImportForm, SearchForm
from project.models import FileSearch
from sample.models import Sample
from ..models.value import Value
from ..serializer import ValueSerializer
from ..forms import ValueAddForm, ValueUpdateForm, ValueGenerateForm, ValueGetForm
import pandas as pd
import numpy as np
import os
import datetime
import zipfile
import requests

class AddView(base.FormView):
    model = Value
    upper = Sample
    form_class = ValueAddForm
    template_name = "project/default_add.html"
    title = 'Value Add'
    success_name = 'value:list'

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        note = form.cleaned_data['note']
        files = form.files.getlist('file')
        delimiter = form.cleaned_data['delimiter']
        encoding = form.cleaned_data['encoding']
        skiprows = form.cleaned_data['skiprows']
        skipends = form.cleaned_data['skipends']
        header = form.cleaned_data['header']
        startstring = form.cleaned_data['startstring']
        endstring = form.cleaned_data['endstring']
        datatype = form.cleaned_data['datatype']
        disp_head = form.cleaned_data['disp_head']
        disp_tail = form.cleaned_data['disp_tail']
        for file in files:
            title = os.path.splitext(os.path.basename(file.name))[0]
            self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                                      title=title, note=note, file=file, delimiter=delimiter, encoding=encoding,
                                      skiprows=skiprows, skipends=skipends, header=header,
                                      startstring=startstring, endstring=endstring,
                                      datatype=datatype, disp_head=disp_head, disp_tail=disp_tail)
        return super().form_valid(form)

class GetView(base.FormView, FileSearch):
    model = Value
    upper = Sample
    form_class = ValueGetForm
    template_name = "project/default_add.html"
    title = 'Value Get'
    success_name = 'value:list'

    def get_file(self, url):
        if url.startswith('http'):
            response = requests.get(url)
            if response.status_code != 200:
                return None
            else:
                data = response.content
        else:
            file = self.file_search(url)
            if file is None:
                return None
            else:
                with file.open('r') as f:
                    data = f.read()
        return InMemoryUploadedFile(ContentFile(data), None,
                                    'Value.csv', None, len(data), None)

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        url = form.cleaned_data['url']
        title = form.cleaned_data['title']
        note = form.cleaned_data['note']
        delimiter = form.cleaned_data['delimiter']
        encoding = form.cleaned_data['encoding']
        skiprows = form.cleaned_data['skiprows']
        skipends = form.cleaned_data['skipends']
        header = form.cleaned_data['header']
        startstring = form.cleaned_data['startstring']
        endstring = form.cleaned_data['endstring']
        datatype = form.cleaned_data['datatype']
        disp_head = form.cleaned_data['disp_head']
        disp_tail = form.cleaned_data['disp_tail']
        file = self.get_file(url)
        if file:
            self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                                      title=title, note=note, file=file, delimiter=delimiter, encoding=encoding,
                                      skiprows=skiprows, skipends=skipends, header=header,
                                      startstring=startstring, endstring=endstring,
                                      datatype=datatype, disp_head=disp_head, disp_tail=disp_tail)
        return super().form_valid(form)

class GenerateView(base.FormView):
    model = Value
    upper = Sample
    form_class = ValueGenerateForm
    template_name = "project/default_add.html"
    title = 'Value Generate'
    success_name = 'value:list'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Val' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        title = form.cleaned_data['title']
        note = form.cleaned_data['note']
        type = form.cleaned_data['type']
        start = form.cleaned_data['start']
        stop = form.cleaned_data['stop']
        step = form.cleaned_data['step']
        num = form.cleaned_data['num']
        low = form.cleaned_data['low']
        high = form.cleaned_data['high']
        mean = form.cleaned_data['mean']
        std = form.cleaned_data['std']
        if int(type) == 0:
            dat = np.arange(start, stop, step)
        elif int(type) == 1:
            dat = np.linspace(start, stop, num)
        elif int(type) == 2:
            dat = np.random.uniform(low, high, num)
        elif int(type) == 3:
            dat = np.random.normal(mean, std, num)
        fname = 'Gen%s.csv' % (base.DateToday()[2:])
        cols = GenerateForm.TYPE_CHOICES[int(type)][1]
        file = base.DataFrame2UploadedFile(pd.DataFrame(dat, columns=[cols]), fname)
        self.model.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                                  title=title, note=note, file=file, skiprows=1)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Value
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'value:add'],
                  ['Get', 'value:get'],
                  ['Generate', 'value:generate'],
                  ['Import', 'value:import'],
                  ['Download', 'value:download'],
                  ['Search', 'value:search']]

class DetailView(base.DetailView):
    model = Value
    template_name = "value/value_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in VALUE_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        return super().get_context_data(**kwargs)

class UpdateView(base.UpdateView):
    model = Value
    form_class = ValueUpdateForm
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Value
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = Value
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class FileView(base.FileView):
    model = Value
    attachment = True
    use_unique = True

class TableView(base.TableView):
    model = Value

class DownloadView(base.View):
    upper = Sample

    def get(self, request, **kwargs):
        sample = self.upper.objects.get(pk=kwargs['pk'])
        images = Value.objects.filter(upper=sample)
        response = HttpResponse(content_type='application/zip')
        zipf = zipfile.ZipFile(response, 'w')
        for image in images:
            basename = os.path.basename(image.file.name)
            zipf.writestr(basename, image.file.read())
        now = datetime.datetime.now()
        filename = 'Values_%s.zip' % (now.strftime('%Y%m%d_%H%M%S'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response

class SearchView(base.SearchView):
    model = Value
    upper = Sample
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Value Search'
    session_name = 'value_search'
    back_name = "value:list"
    lower_items = VALUE_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = ValueSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = Value
    serializer_class = ValueSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Value
    serializer_class = ValueSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Value
    serializer_class = ValueSerializer

class FileAPIView(base_api.FileAPIView):
    model = Value
    attachment = True

class ValueRemote(remote.FileRemote):
    model = Value
    add_name = 'value:api_add'
    list_name = 'value:api_list'
    retrieve_name = 'value:api_retrieve'
    update_name = 'value:api_update'
    file_fields_names = [('file', 'value:api_file')]
    serializer_class = ValueSerializer
    lower_items = VALUE_LOWER

class ImportView(remote.ImportView):
    model = Value
    upper = Sample
    form_class = ImportForm
    remote_class = ValueRemote
    template_name = "project/default_import.html"
    title = 'Value Import'
    success_name = 'value:list'
    view_name = 'value:detail'
    hidden_lower = False
    default_lower = False