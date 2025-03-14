from project.views import base, base_api, remote, prefix
from project.models import Project
from project.forms import ImportForm
from ..models.design import Design
from ..models.condition import Condition
from .condition import ConditionRemote
from .experiment import ExperimentRemote
from ..forms import DesignAddForm, DesignUpdateForm
from ..serializer import DesignSerializer

class AddView(prefix.AddPrefixView):
    model = Design
    upper = Project
    form_class = DesignAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Des' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Design
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'design:add'],
                  ['Import', 'design:import']]

class DetailView(base.DetailView):
    model = Design
    template_name = "design/design_detail.html"
    navigation = [['Experiment', 'design:experiment_list'],]

class UpdateView(prefix.UpdatePrefixView):
    model = Design
    form_class = DesignUpdateForm
    template_name = "design/design_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        condition = Condition.objects.filter(upper=model)
        context['condition'] = condition
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.get_candidates()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Design
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteManagerView):
    model = Design
    template_name = "project/default_delete.html"

class TableView(base.TableView):
    model = Design

class PlotView(base.PlotView):
    model = Design

class DesignSearch(base.Search):
    model = Design
    lower_items = [{'Search': 'design.views.experiment.ExperimentSearch'}]

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = DesignSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Design
    serializer_class = DesignSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Design
    serializer_class = DesignSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Design
    serializer_class = DesignSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Design
    serializer_class = DesignSerializer

class FileAPIView(base_api.FileAPIView):
    model = Design

class DesignRemote(remote.FileRemote):
    model = Design
    add_name = 'design:api_add'
    list_name = 'design:api_list'
    retrieve_name = 'design:api_retrieve'
    update_name = 'design:api_update'
    delete_name = 'design:api_delete'
    file_fields_names = [('file', 'design:api_file')]
    serializer_class = DesignSerializer
    child_remote = [ConditionRemote, ExperimentRemote]

class ImportView(remote.ImportView):
    model = Design
    upper = Project
    form_class = ImportForm
    remote_class = DesignRemote
    template_name = "project/default_import.html"
    title = 'Design Import'
    success_name = 'design:list'
    view_name = 'design:detail'
