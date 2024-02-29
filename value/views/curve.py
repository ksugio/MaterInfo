from django.forms import HiddenInput
from config.settings import VALUE_CURVE_EQUATION
from project.views import base, base_api, remote, prefix
from project.forms import AliasForm, EditNoteForm, ImportForm
from ..models.filter import Filter
from ..models.curve import Curve
from ..models.equation import Equation
from ..forms import CurveAddForm, CurveUpdateForm
from ..serializer import CurveSerializer
from .equation_api import EquationRemote
import json

class AddView(prefix.AddPrefixView):
    model = Curve
    upper = Filter
    form_class = CurveAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Cv' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class AliasView(base.FormView):
    model = Curve
    upper = Filter
    form_class = AliasForm
    template_name = "project/default_add.html"
    title = 'Curve Alias'
    success_name = 'value:curve_list'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        models = self.model.objects.filter(template=True).filter(upper__upper__upper__upper=upper.upper.upper.upper)
        candidate = []
        for model in models:
            title = '%s/%s/%s/%s' % (model.upper.upper.upper.title, model.upper.upper.title, model.upper.title, model.title)
            candidate.append((model.id, title))
        form.fields['template'].choices = candidate
        return form

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        id = form.cleaned_data['template']
        source = self.model.objects.get(id=id)
        title = source.title + ' (Alias)'
        object = self.model.objects.create(
            created_by=self.request.user, updated_by=self.request.user, upper=upper,
            title=title, columnx=source.columnx, columny=source.columny, alias=source.id)
        object.measure()
        object.save()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Curve
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'value:curve_add'],
                  ['Alias', 'value:curve_alias'],
                  ['Import', 'value:curve_import']]

class DetailView(base.DetailView):
    model = Curve
    template_name = "value/curve_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.params:
            context['params'] = json.loads(model.params)
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Curve
    form_class = CurveUpdateForm
    template_name = "value/curve_update.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.alias:
            form.fields['template'].widget = HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        equations = Equation.objects.filter(upper=model)
        context['equation'] = base.Entity(equations)
        add_name = []
        for item in VALUE_CURVE_EQUATION:
            if 'AddName' in item:
                add_name.append(item['AddName'])
        context['equation_add'] = base.NavigationList(add_name, model.id)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Curve
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Curve
    template_name = "project/default_delete.html"

class CurveSearch(base.Search):
    model = Curve

class PlotView(base.PlotView):
    model = Curve

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = CurveSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Curve
    serializer_class = CurveSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Curve
    serializer_class = CurveSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Curve
    serializer_class = CurveSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Curve
    serializer_class = CurveSerializer

class CurveRemote(remote.Remote):
    model = Curve
    add_name = 'value:api_curve_add'
    list_name = 'value:api_curve_list'
    retrieve_name = 'value:api_curve_retrieve'
    update_name = 'value:api_curve_update'
    delete_name = 'value:api_curve_delete'
    serializer_class = CurveSerializer
    child_remote = [EquationRemote]

    def create(self, data, upper, user, **kwargs):
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.filter(upper__upper__upper__upper=upper.upper.upper.upper).filter(remoteid=data['alias'])
            if source:
                data['alias'] = source[0].id
            else:
                data['alias'] = None
        return super().create(data, upper, user, **kwargs)

    def update(self, model, data, user, **kwargs):
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.filter(upper__upper__upper__upper=model.upper.upper.upper.upper).filter(remoteid=data['alias'])
            if source:
                data['alias'] = source[0].id
            else:
                data['alias'] = None
        return super().update(model, data, user, **kwargs)

    def data_files(self, model, data, files, **kwargs):
        model, data, files, kwargs = super().data_files(model, data, files, **kwargs)
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.get(id=data['alias'])
            data['alias'] = source.remoteid
        return model, data, files, kwargs

class ImportView(remote.ImportView):
    model = Curve
    upper = Filter
    form_class = ImportForm
    remote_class = CurveRemote
    template_name = "project/default_import.html"
    title = 'Curve Import'
    success_name = 'value:curve_list'
    view_name = 'value:curve_detail'
