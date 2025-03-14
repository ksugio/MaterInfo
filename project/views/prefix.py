from django.db.models import Q
from django.utils.module_loading import import_string
from config.settings import COLLECT_FEATURES
from project.views import base, base_api, remote
from project.models import Project, Prefix
from sample.models import Sample
from ..forms import ImportForm
from ..serializer import PrefixSerializer
import json

class AddView(base.AddView):
    model = Prefix
    upper = Project
    fields = ('prefix', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Prefix
    upper = Project
    template_name = "project/prefix_list.html"
    navigation = [['Add', 'project:prefix_add'],
                  ['Import', 'project:prefix_import']]
    paginate_by = 12

class DetailView(base.DetailView):
    model = Prefix
    template_name = "project/prefix_detail.html"

    def prefix_features(self, model):
        features = []
        for samp in Sample.objects.all():
            expr = samp.get_experiment()
            if expr:
                columns = json.loads(expr.upper.columns)
                if model.unique in columns:
                    features.append(samp)
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if hasattr(cls, 'prefix'):
                if item['Depth'] == 2:
                    feats = cls.objects.filter(upper__upper=model.upper, prefix=model.unique)
                elif item['Depth'] == 3:
                    feats = cls.objects.filter(upper__upper__upper=model.upper, prefix=model.unique)
                elif item['Depth'] == 4:
                    feats = cls.objects.filter(upper__upper__upper__upper=model.upper, prefix=model.unique)
                for feat in feats:
                    features.append(feat)
        return features

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['features'] = self.prefix_features(model)
        return context

class UpdateView(base.UpdateView):
    model = Prefix
    fields = ('prefix', 'note')
    template_name = "project/default_update.html"

class EditNoteView(base.MDEditView):
    model = Prefix
    text_field = 'note'
    template_name = "project/default_mdedit.html"

# Prefix Default Class
class AddPrefixView(base.AddView):
    model = None
    upper = None
    template_name = "project/default_add.html"
    disp_default = True

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        project = base.ProjectModel(upper)
        prefix = Prefix.objects.filter(upper=project)
        if self.disp_default:
            if self.model.default_prefix:
                choices = [('000000', self.model.default_prefix)]
            else:
                choices = [('000000', self.model.__name__)]
        else:
            choices = []
        for p in prefix:
            choices.append((p.unique, p.prefix))
        form = super().get_form(form_class=form_class)
        form.fields['prefix'].choices = choices
        return form

class UpdatePrefixView(base.UpdateView):
    model = None
    template_name = "project/default_update.html"
    disp_default = True

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        project = base.ProjectModel(model)
        prefix = Prefix.objects.filter(upper=project)
        if self.disp_default:
            if self.model.default_prefix:
                choices = [('000000', self.model.default_prefix)]
            else:
                choices = [('000000', self.model.__name__)]
        else:
            choices = []
        for p in prefix:
            choices.append((p.unique, p.prefix))
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
    upper = Project
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

class ImportView(remote.ImportView):
    model = Prefix
    upper = Project
    form_class = ImportForm
    remote_class = PrefixRemote
    template_name = "project/default_import.html"
    title = 'Prefix Import'
    success_name = 'prefix:list'
    view_name = 'prefix:detail'