from django.shortcuts import render
from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.classification import Classification
from ..models.classshap import ClassSHAP
from ..serializer import ClassSHAPSerializer
import json

class AddView(base.AddView):
    model = ClassSHAP
    upper = Classification
    fields = ('title', 'note', 'test_size')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'CSH' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.explain()
        return super().form_valid(form)

class ListView(base.ListView):
    model = ClassSHAP
    upper = Classification
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:classshap_add'],]

class DetailView(base.DetailView):
    model = ClassSHAP
    template_name = "collect/classshap_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
    model = ClassSHAP
    fields = ('title', 'status', 'note', 'test_size')
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.explain()
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = ClassSHAP
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = ClassSHAP
    template_name = "project/default_delete.html"

class PlotView(base.PlotView):
    model = ClassSHAP

class PlotDependenceView(base.PlotView):
    model = ClassSHAP
    methods = 'plot_dependence'

# API
class AddAPIView(base_api.AddAPIView):
    upper = Classification
    serializer_class = ClassSHAPSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Classification
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = ClassSHAP
    serializer_class = ClassSHAPSerializer

class ClassSHAPRemote(remote.Remote):
    model = ClassSHAP
    add_name = 'collect:api_classshap_add'
    list_name = 'collect:api_classshap_list'
    retrieve_name = 'collect:api_classshap_retrieve'
    update_name = 'collect:api_classshap_update'
    delete_name = 'collect:api_classshap_delete'
    serializer_class = ClassSHAPSerializer
