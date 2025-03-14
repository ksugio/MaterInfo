from django.http import HttpResponse
from project.views import base, base_api, remote, task
from ..models.filter import Filter
from ..models.regression import Regression
from ..forms import RegressionAddForm, RegressionUpdateForm
from ..tasks import RegressionTask
from ..serializer import RegressionSerializer
from .regreshap import RegreSHAPRemote
from .regrepred import RegrePredRemote
import json
import datetime

class AddView(task.AddView):
    model = Regression
    upper = Filter
    form_class = RegressionAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Reg' + base.DateToday()[2:]
        form.fields['objective'].choices = upper.columns_choice(drophead=True)
        form.columns_text = upper.columns_text
        return form

    def start_task(self, form, model):
        features, obj = model.dataset()
        if features is not None:
            model.task_id = RegressionTask.delay(
                features.values.tolist(), obj.values.tolist(),
                model.hparam, form.cleaned_data['optimize'],
                model.testsize, model.randomts, model.scaler,
                model.pca, model.get_n_components(features),
                model.method, model.nsplits, model.random, model.ntrials,
                features.columns.tolist(),
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = Regression
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:regression_add'],]

class DetailView(task.DetailView):
    model = Regression
    template_name = "collect/regression_detail.html"
    result_fields = ('results',)
    navigation = [['RegreSHAP', 'collect:regreshap_list'],
                  ['RegrePred', 'collect:regrepred_list']]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.result_saved(model):
            context['results'] = json.loads(model.results)
        return context

class UpdateView(task.UpdateView):
    model = Regression
    form_class = RegressionUpdateForm
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['objective'].choices = model.upper.columns_choice(drophead=True)
        form.fields['objective'].initial = model.objective
        form.columns_text = model.upper.columns_text
        return form

    def start_task(self, form, model):
        features, obj = model.dataset()
        if features is not None:
            model.task_id = RegressionTask.delay(
                features.values.tolist(), obj.values.tolist(),
                model.hparam, form.cleaned_data['optimize'],
                model.testsize, model.randomts, model.scaler,
                model.pca, model.get_n_components(features),
                model.method, model.nsplits, model.random, model.ntrials,
                features.columns.tolist(),
                request_user_id=self.request.user.id
            )
            model.results = ''
            if model.file:
                model.file.delete()
            if model.file2:
                model.file2.delete()

class EditNoteView(base.MDEditView):
    model = Regression
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = Regression
    template_name = "project/default_delete.html"

class RevokeView(task.RevokeView):
    model = Regression
    template_name = "project/default_revoke.html"
    success_name = 'collect:regression_detail'

class ONNXView(base.View):
    model = Regression

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        onnx, mse_onnx = model.to_onnx()
        if mse_onnx < 1.0e-3:
            response = HttpResponse(onnx, content_type='text/plain; charset=Shift-JIS')
            now = datetime.datetime.now()
            filename = 'Regression_%s.onnx' % (now.strftime('%Y%m%d_%H%M%S'))
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
            return response
        else:
            return HttpResponse('Cannot transform to ONNX')

class FileView(base.FileView):
    model = Regression
    attachment = True
    use_unique = True

class File2View(base.FileView):
    model = Regression
    attachment = True
    field = 'file2'

class PlotView(base.PlotView):
    model = Regression

class PlotAllView(base.PlotView):
    model = Regression
    methods = 'plot_all'

class PlotImportanceView(base.PlotView):
    model = Regression
    methods = 'plot_importance'

class PlotTrialsView(base.PlotView):
    model = Regression
    methods = 'plot_trials'

class RegressionSearch(base.Search):
    model = Regression

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = RegressionSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Regression
    serializer_class = RegressionSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Regression
    serializer_class = RegressionSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Regression
    serializer_class = RegressionSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Regression
    serializer_class = RegressionSerializer

class FileAPIView(base_api.FileAPIView):
    model = Regression

class File2APIView(base_api.FileAPIView):
    model = Regression
    field = 'file2'

class RegressionRemote(remote.FileRemote):
    model = Regression
    add_name = 'collect:api_regression_add'
    list_name = 'collect:api_regression_list'
    retrieve_name = 'collect:api_regression_retrieve'
    update_name = 'collect:api_regression_update'
    delete_name = 'collect:api_regression_delete'
    file_fields_names = [('file', 'collect:api_regression_file'),
                         ('file2', 'collect:api_regression_file2')]
    serializer_class = RegressionSerializer
    lower_remote = [RegreSHAPRemote, RegrePredRemote]

