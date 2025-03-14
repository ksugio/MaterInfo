import pandas as pd
from django.http import HttpResponse
from project.views import base, base_api, remote
from ..models.filter import Filter
from ..models.correlation import Correlation
from ..serializer import CorrelationSerializer

class AddView(base.AddView):
    model = Correlation
    upper = Filter
    fields = ('title', 'note', 'method', 'drop', 'mincorr',
              'sizex', 'sizey', 'colormap', 'colorbar', 'annotate', 'label')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Corr' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.calc_corr()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Correlation
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:correlation_add'],]

class DetailView(base.DetailView):
    model = Correlation
    template_name = "collect/correlation_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['corr_list'] = model.corr_list()
        return context

class UpdateView(base.UpdateView):
    model = Correlation
    fields = ('title', 'status', 'note', 'method', 'drop', 'mincorr',
              'sizex', 'sizey', 'colormap', 'colorbar', 'annotate', 'label')
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.calc_corr()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Correlation
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Correlation
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Correlation
    attachment = True

class HeatmapView(base.PlotView):
    model = Correlation
    methods = 'plot_heatmap'

class ScatterView(base.PlotView):
    model = Correlation
    methods = 'plot_scatter'

class CorrelationSearch(base.Search):
    model = Correlation

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = CorrelationSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Correlation
    serializer_class = CorrelationSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Correlation
    serializer_class = CorrelationSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Correlation
    serializer_class = CorrelationSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Correlation
    serializer_class = CorrelationSerializer

class FileAPIView(base_api.FileAPIView):
    model = Correlation

class CorrelationRemote(remote.FileRemote):
    model = Correlation
    add_name = 'collect:api_correlation_add'
    list_name = 'collect:api_correlation_list'
    retrieve_name = 'collect:api_correlation_retrieve'
    update_name = 'collect:api_correlation_update'
    delete_name = 'collect:api_correlation_delete'
    file_fields_names = [('file', 'collect:api_correlation_file')]
    serializer_class = CorrelationSerializer

