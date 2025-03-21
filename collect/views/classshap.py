from django.shortcuts import render
from project.views import base, base_api, remote, task
from ..models.classification import Classification
from ..models.classshap import ClassSHAP
from ..tasks import ClassSHAPTask
from ..serializer import ClassSHAPSerializer
import json

class AddView(task.AddView):
    model = ClassSHAP
    upper = Classification
    fields = ('title', 'note', 'use_kernel', 'kmeans', 'nsample')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'CSH' + base.DateToday()[2:]
        return form

    def start_task(self, form, model):
        features, obj = model.upper.dataset(shuffle=True)
        if features is not None:
            model.task_id = ClassSHAPTask.delay(
                model.upper.read_model(raw_data=True),
                features.values.tolist(), obj.values.tolist(),
                features.columns.tolist(),
                model.use_kernel, model.kmeans, model.nsample,
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = ClassSHAP
    upper = Classification
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:classshap_add'],]

class DetailView(task.DetailView):
    model = ClassSHAP
    template_name = "collect/classshap_detail.html"
    result_fields = ('results',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.result_saved(model):
            context['results'] = json.loads(model.results)
        return context

class UpdateView(task.UpdateView):
    model = ClassSHAP
    fields = ('title', 'status', 'note', 'use_kernel', 'kmeans', 'nsample')
    template_name = "project/default_update.html"

    def start_task(self, form, model):
        features, obj = model.upper.dataset(shuffle=True)
        if features is not None:
            model.task_id = ClassSHAPTask.delay(
                model.upper.read_model(raw_data=True),
                features.values.tolist(), obj.values.tolist(),
                features.columns.tolist(),
                model.use_kernel, model.kmeans, model.nsample,
                request_user_id=self.request.user.id
            )
            model.results = ''

class EditNoteView(base.MDEditView):
    model = ClassSHAP
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = ClassSHAP
    template_name = "project/default_delete.html"

class RevokeView(task.RevokeView):
    model = ClassSHAP
    template_name = "project/default_revoke.html"
    success_name = 'collect:classshap_detail'

class PlotView(base.PlotView):
    model = ClassSHAP

class PlotDependenceView(base.PlotView):
    model = ClassSHAP
    methods = 'plot_dependence'

# API
class AddAPIView(base_api.AddAPIView):
    upper = Classification
    serializer_class = ClassSHAPSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Classification
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class ClassSHAPRemote(remote.Remote):
    model = ClassSHAP
    add_name = 'collect:api_classshap_add'
    list_name = 'collect:api_classshap_list'
    retrieve_name = 'collect:api_classshap_retrieve'
    update_name = 'collect:api_classshap_update'
    delete_name = 'collect:api_classshap_delete'
    serializer_class = ClassSHAPSerializer
