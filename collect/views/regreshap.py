from django.shortcuts import render
from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.regression import Regression
from ..models.regreshap import RegreSHAP
from ..serializer import RegreSHAPSerializer
import json

class AddView(base.AddView):
    model = RegreSHAP
    upper = Regression
    fields = ('title', 'note', 'test_size')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'RSH' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.explain()
        return super().form_valid(form)

class ListView(base.ListView):
    model = RegreSHAP
    upper = Regression
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:regreshap_add'],]

class DetailView(base.DetailView):
    model = RegreSHAP
    template_name = "collect/regreshap_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
    model = RegreSHAP
    fields = ('title', 'status', 'note', 'test_size')
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.explain()
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = RegreSHAP
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = RegreSHAP
    template_name = "project/default_delete.html"

class PlotView(base.PlotView):
    model = RegreSHAP

class PlotDependenceView(base.PlotView):
    model = RegreSHAP
    methods = 'plot_dependence'

# API
class AddAPIView(base_api.AddAPIView):
    upper = Regression
    serializer_class = RegreSHAPSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Regression
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = RegreSHAP
    serializer_class = RegreSHAPSerializer

class RegreSHAPRemote(remote.Remote):
    model = RegreSHAP
    add_name = 'collect:api_regreshap_add'
    list_name = 'collect:api_regreshap_list'
    retrieve_name = 'collect:api_regreshap_retrieve'
    update_name = 'collect:api_regreshap_update'
    delete_name = 'collect:api_regreshap_delete'
    serializer_class = RegreSHAPSerializer
