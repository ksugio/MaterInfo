from django.utils.module_loading import import_string
from config.settings import SAMPLE_LOWER
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from .models import Sample
from .serializer import SampleSerializer

class AddView(base.AddView):
    model = Sample
    upper = Project
    fields = ('title', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Sample
    upper = Project
    template_name = "project/default_list.html"
    change_order = True
    change_paginate = True
    navigation = [['Add', 'sample:add'],
                  ['Import', 'sample:import'],
                  ['Clone', 'sample:clone'],
                  ['Search', 'sample:search']]

class DetailView(base.DetailView):
    model = Sample
    template_name = "sample/sample_detail.html"

    def get_context_data(self, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        self.navigation = []
        lowers = []
        for item in SAMPLE_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
            if 'Search' in item:
                cls = import_string(item['Search'])
                for item in cls.model.objects.filter(upper=model):
                    lowers.append({'name': cls.model.__name__, 'item': item})
        context = super().get_context_data(**kwargs)
        if lowers:
            context['lowers'] = lowers
        if model.design:
            condition = model.get_condition()
            context['condition'] = condition
            context['condition_keys'] = condition.keys()
        return context

class UpdateView(base.UpdateView):
    model = Sample
    fields = ('title', 'status', 'note')
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Sample
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Sample
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class SearchView(base.SearchView):
    model = Sample
    upper = Project
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Sample Search'
    session_name = 'sample_search'
    back_name = "sample:list"
    lower_items = SAMPLE_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = SampleSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Sample
    serializer_class = SampleSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Sample
    serializer_class = SampleSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Sample
    serializer_class = SampleSerializer

class SampleRemote(remote.Remote):
    model = Sample
    add_name = 'sample:api_add'
    list_name = 'sample:api_list'
    retrieve_name = 'sample:api_retrieve'
    update_name = 'sample:api_update'
    serializer_class = SampleSerializer
    lower_items = SAMPLE_LOWER

class ImportView(remote.ImportView):
    model = Sample
    upper = Project
    form_class = ImportForm
    remote_class = SampleRemote
    remote_name = 'sample.views.SampleRemote'
    upper_name = 'project.models.Project'
    template_name = "project/default_import.html"
    title = 'Sample Import'
    success_name = 'sample:list'
    success_kwargs = {'order': 0, 'size': 0}
    view_name = 'sample:detail'
    hidden_lower = False
    default_lower = True

class CloneView(remote.CloneView):
    model = Sample
    upper = Project
    form_class = CloneForm
    remote_class = SampleRemote
    remote_name = 'sample.views.SampleRemote'
    upper_name = 'project.models.Project'
    template_name = "project/default_clone.html"
    title = 'Sample Clone'
    success_name = 'sample:list'
    success_kwargs = {'order': 0, 'size': 0}
    view_name = 'sample:detail'

class TokenView(remote.TokenView):
    model = Sample
    form_class = TokenForm
    success_names = ['sample:pull', 'sample:push']

class PullView(remote.PullView):
    model = Sample
    remote_class = SampleRemote
    success_name = 'sample:detail'
    fail_name = 'sample:token'

class PushView(remote.PushView):
    model = Sample
    remote_class = SampleRemote
    success_name = 'sample:detail'
    fail_name = 'sample:token'

class LogView(remote.LogView):
    model = Sample

class SetRemoteView(remote.SetRemoteView):
    model = Sample
    form_class = SetRemoteForm
    remote_class = SampleRemote
    title = 'Sample Set Remote'
    success_name = 'sample:detail'
    view_name = 'sample:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Sample
    remote_class = SampleRemote
    success_name = 'sample:detail'
