from project.views import base, base_api, remote, prefix
from project.forms import EditNoteForm, ImportForm
from sample.models import Sample
from ..models import Material, Element
from ..forms import MaterialAddForm, MaterialUpdateForm
from ..serializer import MaterialSerializer
from .element import ElementRemote

class AddView(prefix.AddPrefixView):
    model = Material
    upper = Sample
    form_class = MaterialAddForm
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Material
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'material:add'],
                  ['Import', 'material:import']]

class DetailView(base.DetailView):
    model = Material
    template_name = "material/material_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['composition'] = model.composition()
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Material
    form_class = MaterialUpdateForm
    template_name = "material/material_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        element = Element.objects.filter(upper=model).order_by('element')
        context['element'] = element
        return context

class DeleteView(base.DeleteManagerView):
    model = Material
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = Material
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class FileView(base.FileView):
    model = Material
    attachment = False

class MaterialSearch(base.Search):
    model = Material

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = MaterialSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = Material
    serializer_class = MaterialSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Material
    serializer_class = MaterialSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Material
    serializer_class = MaterialSerializer

class FileAPIView(base_api.FileAPIView):
    model = Material
    attachment = False

class MaterialRemote(remote.FileRemote):
    model = Material
    add_name = 'material:api_add'
    list_name = 'material:api_list'
    retrieve_name = 'material:api_retrieve'
    update_name = 'material:api_update'
    file_fields_names = [('file', 'material:api_file')]
    serializer_class = MaterialSerializer
    child_remote = [ElementRemote]

class ImportView(remote.ImportView):
    model = Material
    upper = Sample
    form_class = ImportForm
    remote_class = MaterialRemote
    template_name = "project/default_import.html"
    title = 'Material Import'
    success_name = 'material:list'
    view_name = 'material:detail'
