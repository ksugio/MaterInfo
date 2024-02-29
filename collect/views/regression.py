from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.filter import Filter
from ..models.regression import Regression
from ..forms import RegressionAddForm, RegressionUpdateForm
from ..serializer import RegressionSerializer
from .regreshap import RegreSHAPRemote
import json

class AddView(base.AddView):
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

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.test_train(optimize)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Regression
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:regression_add'],]

class DetailView(base.DetailView):
    model = Regression
    template_name = "collect/regression_detail.html"
    navigation = [['RegreSHAP', 'collect:regreshap_list'], ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
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

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        optimize = form.cleaned_data['optimize']
        model.test_train(optimize)
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Regression
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Regression
    template_name = "project/default_delete.html"

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
    lower_remote = [RegreSHAPRemote]
