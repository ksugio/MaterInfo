from django.http import HttpResponse
from django.shortcuts import render, redirect
from config.settings import COLLECT_LOWER
from project.views import base, base_api, remote
from project.models import Project
from project.forms import EditNoteForm, SearchForm, ImportForm, CloneForm, TokenForm, SetRemoteForm
from ..models.collect import Collect
from ..forms import CollectUpdateForm, CollectUploadForm
from ..serializer import CollectSerializer
from .filter import FilterRemote

class AddView(base.AddView):
    model = Collect
    upper = Project
    fields = ('title', 'note', 'projectids', 'disp_head', 'disp_tail')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Collect' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.collect_features(self.request.user)
        return super().form_valid(form)

class UploadView(base.AddView):
    model = Collect
    upper = Project
    form_class = CollectUploadForm
    template_name ="project/default_add.html"
    title = 'Collect Upload'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Collect' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.upload(form.cleaned_data['uploadfile'])
        return super().form_valid(form)

class ListView(base.ListView):
    model = Collect
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:add'],
                  ['Import', 'collect:import'],
                  ['Clone', 'collect:clone'],
                  ['Upload', 'collect:upload'],
                  ['Search', 'collect:search']]

class DetailView(base.DetailView):
    model = Collect
    template_name = "collect/collect_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in COLLECT_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        overview = []
        for item in model.overview_text.split(','):
            overview.append(item.split(':'))
        context['head'] = overview[:4]
        context['feature'] = overview[4:]
        return context

class UpdateView(base.UpdateView):
    model = Collect
    form_class = CollectUpdateForm
    template_name = "collect/collect_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        #context['features'] = model.upper_updated_features(self.request.user)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if form.cleaned_data['collect']:
            model.collect_features(self.request.user)
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Collect
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Collect
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Collect
    attachment = True

class FeatureUpdateView(base.View):
    model = Collect
    template_name = "collect/feature_update.html"
    success_name = "collect:update"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        features = model.upper_updated_features(request.user)
        params = {
            'object': model,
            'features': features,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        model.upper_updated_measure_features(request.user)
        return redirect(model.get_update_url())

class TableView(base.TableView):
    model = Collect

class SearchView(base.SearchView):
    model = Collect
    upper = Project
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Collect Search'
    session_name = 'collect_search'
    back_name = "collect:list"
    lower_items = COLLECT_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = CollectSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Collect
    serializer_class = CollectSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Collect
    serializer_class = CollectSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Collect
    serializer_class = CollectSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Collect
    serializer_class = CollectSerializer

class FileAPIView(base_api.FileAPIView):
    model = Collect

class CollectRemote(remote.FileRemote):
    model = Collect
    add_name = 'collect:api_add'
    list_name = 'collect:api_list'
    retrieve_name = 'collect:api_retrieve'
    update_name = 'collect:api_update'
    delete_name = 'collect:api_delete'
    file_fields_names = [('file', 'collect:api_file')]
    serializer_class = CollectSerializer
    lower_items = COLLECT_LOWER

class ImportView(remote.ImportView):
    model = Collect
    upper = Project
    form_class = ImportForm
    remote_class = CollectRemote
    template_name = "project/default_import.html"
    title = 'Collect Import'
    success_name = 'collect:list'
    view_name = 'collect:detail'
    hidden_lower = False
    default_lower = False

class CloneView(remote.CloneView):
    model = Collect
    form_class = CloneForm
    upper = Project
    remote_class = CollectRemote
    template_name = "project/default_clone.html"
    title = 'Collect Clone'
    success_name = 'collect:list'
    view_name = 'collect:detail'

class TokenView(remote.TokenView):
    model = Collect
    form_class = TokenForm
    success_names = ['collect:pull', 'collect:push']

class PullView(remote.PullView):
    model = Collect
    remote_class = CollectRemote
    success_name = 'collect:detail'
    fail_name = 'collect:token'

class PushView(remote.PushView):
    model = Collect
    remote_class = CollectRemote
    success_name = 'collect:detail'
    fail_name = 'collect:token'

class SetRemoteView(remote.SetRemoteView):
    model = Collect
    form_class = SetRemoteForm
    remote_class = CollectRemote
    title = 'Collect Set Remote'
    success_name = 'collect:detail'
    view_name = 'collect:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Collect
    remote_class = CollectRemote
    success_name = 'collect:detail'
