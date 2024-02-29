from django.shortcuts import render, redirect
from config.settings import SAMPLE_LOWER
from project.views import base, base_api, remote
from project.models import Project
from project.forms import EditNoteForm, ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
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
    navigation = [['Add', 'sample:add'],
                  ['Import', 'sample:import'],
                  ['Clone', 'sample:clone'],
                  ['Search', 'sample:search']]

class DetailView(base.DetailView):
    model = Sample
    template_name = "sample/sample_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in SAMPLE_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        return super().get_context_data(**kwargs)

class UpdateView(base.UpdateView):
    model = Sample
    fields = ('title', 'status', 'note')
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Sample
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = Sample
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

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
    model = Sample
    upper = Project
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
    template_name = "project/default_import.html"
    title = 'Sample Import'
    success_name = 'sample:list'
    view_name = 'sample:detail'
    hidden_lower = False
    default_lower = True

class CloneView(remote.CloneView):
    model = Sample
    form_class = CloneForm
    upper = Project
    remote_class = SampleRemote
    template_name = "project/default_clone.html"
    title = 'Sample Clone'
    success_name = 'sample:list'
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
