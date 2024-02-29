from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.filter import Filter
from ..models.clustering import Clustering
from ..forms import ClusteringAddForm, ClusteringUpdateForm
from ..serializer import ClusteringSerializer
import json

class AddView(base.AddView):
    model = Clustering
    upper = Filter
    form_class = ClusteringAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Clu' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.train(optimize)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Clustering
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:clustering_add'],]

class DetailView(base.DetailView):
    model = Clustering
    template_name = "collect/clustering_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
    model = Clustering
    form_class = ClusteringUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.train(optimize)
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Clustering
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Clustering
    template_name = "project/default_delete.html"

class PlotView(base.PlotView):
    model = Clustering

class PlotTrialsView(base.PlotView):
    model = Clustering
    methods = 'plot_trials'

class ClusteringSearch(base.Search):
    model = Clustering

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = ClusteringSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Clustering
    serializer_class = ClusteringSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Clustering
    serializer_class = ClusteringSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Clustering
    serializer_class = ClusteringSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Clustering
    serializer_class = ClusteringSerializer

class FileAPIView(base_api.FileAPIView):
    model = Clustering

class ClusteringRemote(remote.FileRemote):
    model = Clustering
    add_name = 'collect:api_clustering_add'
    list_name = 'collect:api_clustering_list'
    retrieve_name = 'collect:api_clustering_retrieve'
    update_name = 'collect:api_clustering_update'
    delete_name = 'collect:api_clustering_delete'
    file_fields_names = [('file', 'collect:api_clustering_file')]
    serializer_class = ClusteringSerializer

