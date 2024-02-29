from django.db.models import Q
from project.views import base, base_api, remote
from project.models import Project, Prefix
from ..forms import EditNoteForm
from ..serializer import PrefixSerializer

class AddView(base.AddView):
    model = Prefix
    upper = Project
    fields = ('prefix', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Prefix
    upper = Project
    template_name = "project/prefix_list.html"
    navigation = [['Add', 'project:prefix_add'],]
    paginate_by = 12

class DetailView(base.DetailView):
    model = Prefix
    template_name = "project/prefix_detail.html"

class UpdateView(base.UpdateView):
    model = Prefix
    fields = ('prefix', 'note')
    template_name = "project/default_update.html"

class EditNoteView(base.EditNoteView):
    model = Prefix
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

# Prefix Default Class
class AddPrefixView(base.AddView):
    model = None
    upper = None
    template_name = "project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        project = base.ProjectModel(upper)
        prefix = Prefix.objects.filter(upper=project)
        if self.model.default_prefix:
            choices = [(0, self.model.default_prefix)]
        else:
            choices = [(0, self.model.__name__)]
        for p in prefix:
            choices.append((p.id, p.prefix))
        form = super().get_form(form_class=form_class)
        form.fields['prefix'].choices = choices
        return form

class UpdatePrefixView(base.UpdateView):
    model = None
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        project = base.ProjectModel(model)
        prefix = Prefix.objects.filter(upper=project)
        if self.model.default_prefix:
            choices = [(0, self.model.default_prefix)]
        else:
            choices = [(0, self.model.__name__)]
        for p in prefix:
            choices.append((p.id, p.prefix))
        form = super().get_form(form_class=form_class)
        form.fields['prefix'].choices = choices
        return form

class PrefixSearch(base.Search):
    model = Prefix

    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(prefix__icontains=text) |
                  Q(note__icontains=text), cond)
        return q

# API
class AddAPIView(base_api.AddAPIView):
    upper = Prefix
    serializer_class = PrefixSerializer

class ListAPIView(base_api.ListAPIView):
    model = Prefix
    upper = Project
    serializer_class = PrefixSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Prefix
    serializer_class = PrefixSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Prefix
    serializer_class = PrefixSerializer

class PrefixRemote(remote.Remote):
    model = Prefix
    add_name = 'project:api_prefix_add'
    list_name = 'project:api_prefix_list'
    retrieve_name = 'project:api_prefix_retrieve'
    update_name = 'project:api_prefix_update'
    serializer_class = PrefixSerializer
