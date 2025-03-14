from project.views import base, base_api, remote, task
from ..models.filter import Filter
from ..models.clustering import Clustering
from ..forms import ClusteringAddForm, ClusteringUpdateForm
from ..tasks import ClusteringTask
from ..serializer import ClusteringSerializer
import json

class AddView(task.AddView):
    model = Clustering
    upper = Filter
    form_class = ClusteringAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Clu' + base.DateToday()[2:]
        return form

    def start_task(self, form, model):
        features = model.dataset()
        if features is not None:
            model.task_id = ClusteringTask.delay(
                features.values.tolist(), model.hparam, form.cleaned_data['optimize'],
                model.scaler, model.n_components,
                model.reduction, model.method, model.score, model.ntrials,
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = Clustering
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:clustering_add'],]

class DetailView(task.DetailView):
    model = Clustering
    result_fields = ('results',)
    template_name = "collect/clustering_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.results:
            context['results'] = json.loads(model.results)
        return context

class UpdateView(task.UpdateView):
    model = Clustering
    form_class = ClusteringUpdateForm
    template_name = "project/default_update.html"

    def start_task(self, form, model):
        features = model.dataset()
        if features is not None:
            model.task_id = ClusteringTask.delay(
                features.values.tolist(), model.hparam, form.cleaned_data['optimize'],
                model.scaler, model.n_components,
                model.reduction, model.method, model.score, model.ntrials,
                request_user_id=self.request.user.id
            )
        model.results = ''
        if model.file:
            model.file.delete()

class EditNoteView(base.MDEditView):
    model = Clustering
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = Clustering
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Clustering
    attachment = True
    use_unique = True

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

