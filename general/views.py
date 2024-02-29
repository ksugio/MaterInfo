from project.views import base, base_api, remote, prefix
from project.forms import EditNoteForm, ImportForm
from sample.models import Sample
from .models import General
from .forms import GeneralAddForm, GeneralUpdateForm
from .serializer import GeneralSerializer

class AddView(prefix.AddPrefixView):
    model = General
    upper = Sample
    form_class = GeneralAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Gen' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = General
    upper = Sample
    template_name = "project/default_list.html"
    navigation = [['Add', 'general:add'],
                  ['Import', 'general:import']]

class DetailView(base.DetailView):
    model = General
    template_name = "general/general_detail.html"
    navigation = []

class UpdateView(prefix.UpdatePrefixView):
    model = General
    form_class = GeneralUpdateForm
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = General
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = General
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class GeneralSearch(base.Search):
    model = General

# API
class AddAPIView(base_api.AddAPIView):
    upper = Sample
    serializer_class = GeneralSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Sample
    model = General
    serializer_class = GeneralSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = General
    serializer_class = GeneralSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = General
    serializer_class = GeneralSerializer

class GeneralRemote(remote.Remote):
    model = General
    add_name = 'general:api_add'
    list_name = 'general:api_list'
    retrieve_name = 'general:api_retrieve'
    update_name = 'general:api_update'
    serializer_class = GeneralSerializer

class ImportView(remote.ImportView):
    model = General
    upper = Sample
    form_class = ImportForm
    remote_class = GeneralRemote
    template_name = "project/default_import.html"
    title = 'General Import'
    success_name = 'general:list'
    view_name = 'general:detail'
