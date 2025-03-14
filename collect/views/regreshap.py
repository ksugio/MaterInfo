from project.views import base, base_api, remote, task
from ..models.regression import Regression
from ..models.regreshap import RegreSHAP
from ..tasks import RegreSHAPTask
from ..serializer import RegreSHAPSerializer
import json

class AddView(task.AddView):
    model = RegreSHAP
    upper = Regression
    fields = ('title', 'note', 'use_kernel', 'kmeans', 'nsample')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'RSH' + base.DateToday()[2:]
        return form

    def start_task(self, form, model):
        features, obj = model.upper.dataset(shuffle=True)
        if features is not None:
            model.task_id = RegreSHAPTask.delay(
                model.upper.read_model(raw_data=True),
                features.values.tolist(), obj.values.tolist(),
                features.columns.tolist(),
                model.use_kernel, model.kmeans, model.nsample,
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = RegreSHAP
    upper = Regression
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:regreshap_add'],]

class DetailView(task.DetailView):
    model = RegreSHAP
    template_name = "collect/regreshap_detail.html"
    result_fields = ('results',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.result_saved(model):
            context['results'] = json.loads(model.results)
        return context

class UpdateView(task.UpdateView):
    model = RegreSHAP
    fields = ('title', 'status', 'note', 'use_kernel', 'kmeans', 'nsample')
    template_name = "project/default_update.html"

    def start_task(self, form, model):
        features, obj = model.upper.dataset(shuffle=True)
        if features is not None:
            model.task_id = RegreSHAPTask.delay(
                model.upper.read_model(raw_data=True),
                features.values.tolist(), obj.values.tolist(),
                features.columns.tolist(),
                model.use_kernel, model.kmeans, model.nsample,
                request_user_id=self.request.user.id
            )
            model.results = ''

class EditNoteView(base.MDEditView):
    model = RegreSHAP
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = RegreSHAP
    template_name = "project/default_delete.html"

class RevokeView(task.RevokeView):
    model = RegreSHAP
    template_name = "project/default_revoke.html"
    success_name = 'collect:regreshap_detail'

class PlotView(base.PlotView):
    model = RegreSHAP

class PlotDependenceView(base.PlotView):
    model = RegreSHAP
    methods = 'plot_dependence'

# API
class AddAPIView(base_api.AddAPIView):
    upper = Regression
    serializer_class = RegreSHAPSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Regression
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class RegreSHAPRemote(remote.Remote):
    model = RegreSHAP
    add_name = 'collect:api_regreshap_add'
    list_name = 'collect:api_regreshap_list'
    retrieve_name = 'collect:api_regreshap_retrieve'
    update_name = 'collect:api_regreshap_update'
    delete_name = 'collect:api_regreshap_delete'
    serializer_class = RegreSHAPSerializer
