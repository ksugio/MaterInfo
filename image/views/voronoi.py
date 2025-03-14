from django.forms import HiddenInput
from django.http import HttpResponse
from django.urls import reverse
from project.views import base, base_api, remote, prefix
from ..models.filter import Filter
from ..models.voronoi import Voronoi
from ..serializer import VoronoiSerializer
from ..forms import VoronoiPlotForm, VoronoiAddForm, VoronoiUpdateForm
from io import BytesIO
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(prefix.AddPrefixView):
    model = Voronoi
    upper = Filter
    form_class = VoronoiAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Vo' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Voronoi
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:voronoi_add'],]

class DetailView(base.DetailView):
    model = Voronoi
    template_name = "image/voronoi_detail.html"
    plot_name = 'image:voronoi_plot'
    file_name = 'image:voronoi_file'
    edit_note_name = 'image:voronoi_edit_note'
    image_name = 'image:voronoi_image'
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plot_name'] = self.plot_name
        context['file_name'] = self.file_name
        context['edit_note_name'] = self.edit_note_name
        context['image_name'] = self.image_name
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['results'] = json.loads(model.results)
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Voronoi
    form_class = VoronoiUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Voronoi
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Voronoi
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Voronoi
    attachment = True
    use_unique = True

class PlotView(base.FormView):
    model = Voronoi
    template_name = "image/detail_plot.html"
    form_class = VoronoiPlotForm
    success_name = 'image:voronoi_plot'
    image_name = 'image:voronoi_plot_image'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.kwargs['plotid'] == 0:
            form.fields['bins'].widget = HiddenInput()
        else:
            form.fields['bins'].initial = self.kwargs['bins']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'], 'bins': self.kwargs['bins']}
        context['imageurl'] = reverse(self.image_name, kwargs=kwargs)
        context['object'] = self.model.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        self.kwargs['bins'] = form.cleaned_data['bins']
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'], 'bins': self.kwargs['bins']}
        return reverse(self.success_name, kwargs=kwargs)

class PlotImageView(base.View):
    model = Voronoi

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        df = model.read_csv()
        unit = model.upper.upper.get_scaleunit_display()
        plotid = kwargs['plotid']
        bins = kwargs['bins']
        plt.figure()
        if plotid == 0:
            plt.hist(df['VFacet'], bins=10, range=(2.5, 12.5), color='white', edgecolor='black')
            plt.xlabel('VFacet')
            plt.ylabel('Frequency')
        elif plotid == 1:
            plt.hist(df['VArea'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('VArea' + ' / ' + unit + '^2')
            plt.ylabel('Frequency')
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class ImageView(base.ImageView):
    model = Voronoi

class VoronoiSearch(base.Search):
    model = Voronoi

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = VoronoiSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Voronoi
    serializer_class = VoronoiSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Voronoi
    serializer_class =VoronoiSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Voronoi
    serializer_class = VoronoiSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Voronoi
    serializer_class = VoronoiSerializer

class FileAPIView(base_api.FileAPIView):
    model = Voronoi
    attachment = True

class VoronoiRemote(remote.FileRemote):
    model = Voronoi
    add_name = 'image:api_voronoi_add'
    list_name = 'image:api_voronoi_list'
    retrieve_name = 'image:api_voronoi_retrieve'
    update_name = 'image:api_voronoi_update'
    delete_name = 'image:api_voronoi_delete'
    file_fields_names = [('file', 'image:api_voronoi_file')]
    serializer_class = VoronoiSerializer
