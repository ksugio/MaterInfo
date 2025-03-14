from project.views import base, base_api, remote, prefix
from project.forms import ImportForm
from sample.models import Sample
from ..models import Hardness, Value
from ..forms import HardnessAddForm, HardnessUpdateForm
from ..serializer import HardnessSerializer
from .value import ValueRemote

class AddView(prefix.AddPrefixView):
    model = Hardness
    upper = Sample
    form_class = HardnessAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'HV' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Hardness
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'hardness:add'],
                  ['Import', 'hardness:import']]

class DetailView(base.DetailView):
    model = Hardness
    template_name = "hardness/hardness_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['describe'] = model.value_describe()
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Hardness
    form_class = HardnessUpdateForm
    template_name = "hardness/hardness_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        value = Value.objects.filter(upper=model)
        context['value'] = value
        return context

class DeleteView(base.DeleteManagerView):
    model = Hardness
    template_name = "project/default_delete.html"

class MoveView(base.MoveManagerView):
    model = Hardness
    template_name = "project/default_update.html"

class EditNoteView(base.MDEditView):
    model = Hardness
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class HardnessSearch(base.Search):
    model = Hardness

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = HardnessSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = Hardness
    serializer_class = HardnessSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Hardness
    serializer_class = HardnessSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Hardness
    serializer_class = HardnessSerializer

class HardnessRemote(remote.Remote):
    model = Hardness
    add_name = 'hardness:api_add'
    list_name = 'hardness:api_list'
    retrieve_name = 'hardness:api_retrieve'
    update_name = 'hardness:api_update'
    serializer_class = HardnessSerializer
    child_remote = [ValueRemote]

class ImportView(remote.ImportView):
    model = Hardness
    upper = Sample
    form_class = ImportForm
    remote_class = HardnessRemote
    template_name = "project/default_import.html"
    title = 'Hardness Import'
    success_name = 'hardness:list'
    view_name = 'hardness:detail'
