import pandas as pd
from django.http import HttpResponse
from project.views import base, base_api, remote
from project.forms import EditNoteForm
from ..models.filter import Filter
from ..models.reduction import Reduction
from ..forms import ReductionAddForm, ReductionUpdateForm
from ..serializer import ReductionSerializer
import numpy as np
import json

class AddView(base.AddView):
    model = Reduction
    upper = Filter
    form_class = ReductionAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Red' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.fit_transform()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Reduction
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:reduction_add'],]

class DetailView(base.DetailView):
    model = Reduction
    template_name = "collect/reduction_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        results = json.loads(model.results)
        if 'Ratio' in results:
            ratio = results['Ratio']
            cumratio = np.cumsum(ratio)
            context['ratio'] = [('PC{}'.format(i+1), r, c) for i, (r, c) in enumerate(zip(ratio, cumratio))]
        return context

class UpdateView(base.UpdateView):
    model = Reduction
    form_class = ReductionUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.fit_transform()
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Reduction
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Reduction
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Reduction
    attachment = True

class PlotScatterView(base.PlotView):
    model = Reduction
    methods = 'plot_scatter'

class PlotComponentsView(base.PlotView):
    model = Reduction
    methods = 'plot_components'

class ReductionSearch(base.Search):
    model = Reduction

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = ReductionSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Reduction
    serializer_class = ReductionSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Reduction
    serializer_class = ReductionSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Reduction
    serializer_class = ReductionSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Reduction
    serializer_class = ReductionSerializer

class FileAPIView(base_api.FileAPIView):
    model = Reduction

class ReductionRemote(remote.FileRemote):
    model = Reduction
    add_name = 'collect:api_reduction_add'
    list_name = 'collect:api_reduction_list'
    retrieve_name = 'collect:api_reduction_retrieve'
    update_name = 'collect:api_reduction_update'
    delete_name = 'collect:api_reduction_delete'
    file_fields_names = [('file', 'collect:api_reduction_file')]
    serializer_class = ReductionSerializer

