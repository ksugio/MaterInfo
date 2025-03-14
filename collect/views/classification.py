from django.http import HttpResponse
from django.shortcuts import render
from project.views import base, base_api, remote, task
from ..models.filter import Filter
from ..models.classification import Classification
from ..forms import ClassificationAddForm, ClassificationUpdateForm
from ..tasks import ClassificationTask
from ..serializer import ClassificationSerializer
from .classshap import ClassSHAPRemote
import json
import datetime

class AddView(task.AddView):
    model = Classification
    upper = Filter
    form_class = ClassificationAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Cla' + base.DateToday()[2:]
        form.fields['objective'].choices = upper.columns_choice(drophead=True)
        return form

    def start_task(self, form, model):
        features, obj = model.dataset()
        if features is not None and model.check_obj(obj):
            model.task_id = ClassificationTask.delay(
                features.values.tolist(), obj.values.tolist(),
                model.hparam, form.cleaned_data['optimize'],
                model.testsize, model.randomts, model.scaler,
                model.pca, model.get_n_components(features),
                model.method, model.nsplits, model.random, model.ntrials,
                features.columns.tolist(),
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = Classification
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:classification_add'],]

class DetailView(task.DetailView):
    model = Classification
    template_name = "collect/classification_detail.html"
    result_fields = ('results',)
    navigation = [['ClassSHAP', 'collect:classshap_list'],
                  ['ClassPred', 'collect:classpred_list']]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.result_saved(model):
            context['results'] = json.loads(model.results)
        return context

class UpdateView(task.UpdateView):
    model = Classification
    form_class = ClassificationUpdateForm
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['objective'].choices = model.upper.columns_choice(drophead=True)
        form.fields['objective'].initial = model.objective
        return form

    def start_task(self, form, model):
        features, obj = model.dataset()
        if features is not None and model.check_obj(obj):
            model.task_id = ClassificationTask.delay(
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

class EditNoteView(base.MDEditView):
    model = Classification
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = Classification
    template_name = "project/default_delete.html"

class RevokeView(task.RevokeView):
    model = Classification
    template_name = "project/default_revoke.html"
    success_name = 'collect:classification_detail'

class ONNXView(base.View):
    model = Classification

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        onnx, score_onnx = model.to_onnx()
        if score_onnx == 1.0:
            response = HttpResponse(onnx, content_type='text/plain; charset=Shift-JIS')
            now = datetime.datetime.now()
            filename = 'Classification_%s.onnx' % (now.strftime('%Y%m%d_%H%M%S'))
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
            return response
        else:
            return HttpResponse('Cannot transform to ONNX')

class FileView(base.FileView):
    model = Classification
    attachment = True

class PlotImportanceView(base.PlotView):
    model = Classification
    methods = 'plot_importance'

class PlotTrialsView(base.PlotView):
    model = Classification
    methods = 'plot_trials'

class ReportView(base.View):
    model = Classification
    template_name = 'collect/classification_report.html'

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        rid = kwargs['rid']
        results = json.loads(model.results)
        if rid < len(results['reports']):
            report = results['reports'][rid].copy()
            del report['id'], report['accuracy'], report['train_accuracy']
        else:
            report = results['all_report']
            del report['accuracy']
        mavg = report.pop('macro avg')
        wavg = report.pop('weighted avg')
        lreport = []
        for key, val in report.items():
            item = [key, val['precision'], val['recall'], val['f1-score'], val['support']]
            lreport.append(item)
        lreport.append(['macro avg', mavg['precision'], mavg['recall'], mavg['f1-score'], mavg['support']])
        lreport.append(['weighted avg', wavg['precision'], wavg['recall'], wavg['f1-score'], wavg['support']])
        if rid < len(results['reports']):
            title = '%s : KFold%d Report' % (model.title, rid)
        else:
            title = '%s : All Report' % (model.title)
        params = {
            'title': title,
            'report': lreport,
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model),
        }
        return render(request, self.template_name, params)

class ClassificationSearch(base.Search):
    model = Classification

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = ClassificationSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Classification
    serializer_class = ClassificationSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Classification
    serializer_class = ClassificationSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Classification
    serializer_class = ClassificationSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Classification
    serializer_class = ClassificationSerializer

class FileAPIView(base_api.FileAPIView):
    model = Classification

class ClassificationRemote(remote.FileRemote):
    model = Classification
    add_name = 'collect:api_classification_add'
    list_name = 'collect:api_classification_list'
    retrieve_name = 'collect:api_classification_retrieve'
    update_name = 'collect:api_classification_update'
    delete_name = 'collect:api_classification_delete'
    file_fields_names = [('file', 'collect:api_classification_file')]
    serializer_class = ClassificationSerializer
    lower_remote = [ClassSHAPRemote]
