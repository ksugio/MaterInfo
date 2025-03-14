from project.views import base, base_api, remote, prefix
from project.forms import ImportForm
from sample.models import Sample
from ..models import Density, Material
from ..forms import DensityAddForm, DensityUpdateForm
from ..serializer import DensitySerializer

class AddView(prefix.AddPrefixView):
    model = Density
    upper = Sample
    form_class = DensityAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Den' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Density
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'density:add'],
                  ['Import', 'density:import']]

class DetailView(base.DetailView):
    model = Density
    template_name = "density/density_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['relative_density'] = model.relative_density()
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Density
    form_class = DensityUpdateForm
    template_name = "density/density_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        material = Material.objects.filter(upper=model)
        context['material'] = material
        return context

class DeleteView(base.DeleteManagerView):
    model = Density
    template_name = "project/default_delete.html"

class MoveView(base.MoveManagerView):
    model = Density
    template_name = "project/default_update.html"

class EditNoteView(base.MDEditView):
    model = Density
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DensitySearch(base.Search):
    model = Density

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = DensitySerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = Density
    serializer_class = DensitySerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Density
    serializer_class = DensitySerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Density
    serializer_class = DensitySerializer

class DensityRemote(remote.Remote):
    model = Density
    add_name = 'density:api_add'
    list_name = 'density:api_list'
    retrieve_name = 'density:api_retrieve'
    update_name = 'density:api_update'
    serializer_class = DensitySerializer

class ImportView(remote.ImportView):
    model = Density
    upper = Sample
    form_class = ImportForm
    remote_class = DensityRemote
    template_name = "project/default_import.html"
    title = 'Density Import'
    success_name = 'density:list'
    view_name = 'density:detail'