from django.shortcuts import render
from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.filter import Filter
from ..models.classification import Classification
from ..forms import ClassificationAddForm, ClassificationUpdateForm
from ..serializer import ClassificationSerializer
from .classshap import ClassSHAPRemote
import json

class AddView(base.AddView):
    model = Classification
    upper = Filter
    form_class = ClassificationAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Cla' + base.DateToday()[2:]
        form.fields['objective'].choices = upper.columns_choice()
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.test_train(optimize)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Classification
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:classification_add'],]

class DetailView(base.DetailView):
    model = Classification
    template_name = "collect/classification_detail.html"
    navigation = [['ClassSHAP', 'collect:classshap_list'], ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.results:
            context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
    model = Classification
    form_class = ClassificationUpdateForm
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['objective'].choices = model.upper.columns_choice()
        form.fields['objective'].initial = model.objective
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.test_train(optimize)
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Classification
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Classification
    template_name = "project/default_delete.html"

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
        report = results['reports'][rid].copy()
        mavg = report.pop('macro avg')
        wavg = report.pop('weighted avg')
        del report['id'], report['accuracy'], report['train_accuracy']
        lreport = []
        for key, val in report.items():
            item = [key, val['precision'], val['recall'], val['f1-score'], val['support']]
            lreport.append(item)
        lreport.append(['macro avg', mavg['precision'], mavg['recall'], mavg['f1-score'], mavg['support']])
        lreport.append(['weighted avg', wavg['precision'], wavg['recall'], wavg['f1-score'], wavg['support']])
        params = {
            'title': '%s : KFold%d Report' % (model.title, rid),
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
