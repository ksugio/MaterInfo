from django.http import HttpResponse
from config.settings import COLLECT_FILTER_PROCESS, COLLECT_FILTER_LOWER
from project.views import base, base_api, remote
from project.forms import ImportForm
from ..models.collect import Collect
from ..models.filter import Filter
from ..models.process import Process
from ..serializer import FilterSerializer
from .process_api import ProcessRemote
from io import StringIO
import pandas as pd

class AddView(base.AddView):
    model = Filter
    upper = Collect
    fields = ('title', 'note', 'disp_head', 'disp_tail', 'hist_bins')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Fil' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.savefile()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Filter
    upper = Collect
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:filter_add'],
                  ['Import', 'collect:filter_import']]

class DetailView(base.DetailView):
    model = Filter
    template_name = "collect/filter_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in COLLECT_FILTER_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.describe:
            df = pd.read_json(StringIO(model.describe))
            df.index = ['count', 'mean', 'std', 'min', 'quarter', 'half', 'threequarters', 'max']
            describe = []
            for col in df.columns:
                item = df[col].to_dict()
                item['name'] = col
                describe.append(item)
            context['describe'] = describe
            context['ndescribe'] = len(describe)
        return context

class UpdateView(base.UpdateView):
    model = Filter
    fields = ('title', 'status', 'note', 'disp_head', 'disp_tail', 'hist_bins')
    template_name = "collect/filter_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        processes = Process.objects.filter(upper=model).order_by('order')
        processes = base.Entity(processes)
        context['process'] = processes
        add_name = []
        for item in COLLECT_FILTER_PROCESS:
            if 'AddName' in item:
                add_name.append(item['AddName'])
        context['process_add'] = base.NavigationList(add_name, model.id)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.savefile()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Filter
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Filter
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Filter
    attachment = True
    use_unique = True

class TableView(base.TableView):
    model = Filter

class PlotView(base.PlotView):
    model = Filter

class FilterSearch(base.Search):
    model = Filter
    lower_items = COLLECT_FILTER_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Collect
    serializer_class = FilterSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Collect
    model = Filter
    serializer_class = FilterSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Filter
    serializer_class = FilterSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Filter
    serializer_class = FilterSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Filter
    serializer_class = FilterSerializer

class FileAPIView(base_api.FileAPIView):
    model = Filter

class FilterRemote(remote.FileRemote):
    model = Filter
    add_name = 'collect:api_filter_add'
    list_name = 'collect:api_filter_list'
    retrieve_name = 'collect:api_filter_retrieve'
    update_name = 'collect:api_filter_update'
    delete_name = 'collect:api_filter_delete'
    file_fields_names = [('file', 'collect:api_filter_file')]
    serializer_class = FilterSerializer
    child_remote = [ProcessRemote]
    lower_items = COLLECT_FILTER_LOWER

class ImportView(remote.ImportView):
    model = Filter
    upper = Collect
    form_class = ImportForm
    remote_class = FilterRemote
    template_name = "project/default_clone.html"
    title = 'Filter Import'
    success_name = 'collect:filter_list'
    view_name = 'collect:filter_detail'
