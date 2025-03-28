from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
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
    fields = ('title', 'note', 'ncol', 'sizex', 'sizey', 'format')
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

def PlotData(plot, format, **kwargs):
    plt.figure(figsize=(plot.sizex, plot.sizey))
    areas = Area.objects.filter(upper=plot).order_by('order')
    if areas.count() == 0:
        plt.subplot(1,1,1)
        plt.axis('off')
    else:
        nrow = int(m.ceil(len(areas) / plot.ncol))
        i = 1
        for area in areas:
            plt.subplot(nrow, plot.ncol, i)
            AreaPlot(area, **kwargs)
            i = i + 1
    buf = BytesIO()
    plt.savefig(buf, format=format, bbox_inches='tight')
    data = buf.getvalue()
    buf.close()
    plt.close()
    return data

class UpdateView(base.UpdateView):
    model = Plot
    fields = ('title', 'status', 'note', 'ncol', 'sizex', 'sizey', 'format')
    template_name = "plot/plot_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        areas = Area.objects.filter(upper=model).order_by('order')
        context['areas'] = areas
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        kwargs = {
            'request_host': self.request._current_scheme_host,
            'request_cookies': self.request.COOKIES
        }
        if model.format == 0:
            data = PlotData(model, 'svg', **kwargs)
            fname = 'Plot.svg'
        elif model.format == 1:
            data = PlotData(model, 'png', **kwargs)
            fname = 'Plot.png'
        elif model.format == 2:
            data = PlotData(model, 'jpeg', **kwargs)
            fname = 'Plot.jpg'
        elif model.format == 3:
            data = PlotData(model, 'pdf', **kwargs)
            fname = 'Plot.pdf'
        elif model.format == 4:
            data = PlotData(model, 'eps', **kwargs)
            fname = 'Plot.eps'
        model.file = InMemoryUploadedFile(ContentFile(data), None, fname,
                                          None, len(data), None)
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Plot
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Plot
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Plot
    attachment = True
    use_unique = True

class PlotView(base.View):
    model = Plot

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        if model.file:
            if model.format == 0:
                with model.file.open('rb') as f:
                    return HttpResponse(f.read(), content_type='image/svg+xml')
            elif model.format == 1:
                with model.file.open('rb') as f:
                    return HttpResponse(f.read(), content_type='image/png')
            elif model.format == 2:
                with model.file.open('rb') as f:
                    return HttpResponse(f.read(), content_type='image/jpeg')
        response = PlotData(model, 'svg',
                            request_host=self.request._current_scheme_host,
                            request_cookies=self.request.COOKIES)
        return HttpResponse(response, content_type='image/svg+xml')

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
