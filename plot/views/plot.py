from django.http import HttpResponse
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm
from ..models.plot import Plot
from ..models.area import Area
from ..views.area import AreaPlot, AreaRemote
from ..serializer import PlotSerializer
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math as m

class AddView(base.AddView):
    model = Plot
    upper = Project
    fields = ('title', 'note', 'ncol', 'sizex', 'sizey')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Plt' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Plot
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'plot:add'],
                  ['Import', 'plot:import']]

class DetailView(base.DetailView):
    model = Plot
    template_name = "plot/plot_detail.html"
    navigation = []

class UpdateView(base.UpdateView):
    model = Plot
    fields = ('title', 'status', 'note', 'ncol', 'sizex', 'sizey')
    template_name = "plot/plot_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        areas = Area.objects.filter(upper=model).order_by('order')
        context['areas'] = areas
        return context

class EditNoteView(base.MDEditView):
    model = Plot
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Plot
    template_name = "project/default_delete.html"

def PlotPlot(plot, **kwargs):
    areas = Area.objects.filter(upper=plot).order_by('order')
    if areas.count() == 0:
        plt.subplot(1,1,1)
        plt.axis('off')
        return
    nrow = int(m.ceil(len(areas) / plot.ncol))
    i = 1
    for area in areas:
        plt.subplot(nrow, plot.ncol, i)
        AreaPlot(area, **kwargs)
        i = i + 1

class PlotView(base.View):
    model = Plot

    def get(self, request, **kwargs):
        plot = self.model.objects.get(pk=kwargs['pk'])
        plt.figure(figsize=(plot.sizex, plot.sizey))
        PlotPlot(plot, request_host=self.request._current_scheme_host,
                 request_cookies=self.request.COOKIES)
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class PlotSearch(base.Search):
    model = Plot

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = PlotSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Plot
    serializer_class = PlotSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Plot
    serializer_class = PlotSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Plot
    serializer_class = PlotSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Plot
    serializer_class = PlotSerializer

class PlotRemote(remote.Remote):
    model = Plot
    add_name = 'plot:api_add'
    list_name = 'plot:api_list'
    retrieve_name = 'plot:api_retrieve'
    update_name = 'plot:api_update'
    delete_name = 'plot:api_delete'
    serializer_class = PlotSerializer
    child_remote = [AreaRemote]

class ImportView(remote.ImportView):
    model = Plot
    upper = Project
    form_class = ImportForm
    remote_class = PlotRemote
    template_name = "project/default_import.html"
    title = 'Plot Import'
    success_name = 'plot:list'
    view_name = 'plot:detail'
