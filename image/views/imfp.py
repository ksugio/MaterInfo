from django.http import HttpResponse
from django.urls import reverse
from project.views import base, base_api, prefix, remote
from plot.views.item import Item
from ..models.filter import Filter
from ..models.imfp import IMFP
from ..serializer import IMFPSerializer
from ..forms import IMFPPlotForm, IMFPAddForm, IMFPUpdateForm
from io import BytesIO
from random import randint
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(prefix.AddPrefixView):
    model = IMFP
    upper = Filter
    form_class = IMFPAddForm
    template_name ="project/default_add.html"
    title_initial = 'IMFP'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = self.title_initial + base.DateToday()[2:]
        form.fields['randseed'].initial = randint(0, 2147483647)
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class ListView(base.ListView):
    model = IMFP
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:imfp_add'],]

class DetailView(base.DetailView):
    model = IMFP
    template_name = "image/imfp_detail.html"
    plot_name = 'image:imfp_plot'
    file_name = 'image:imfp_file'
    edit_note_name = 'image:imfp_edit_note'
    image_name = 'image:imfp_image'
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plot_name'] = self.plot_name
        context['file_name'] = self.file_name
        context['edit_note_name'] = self.edit_note_name
        context['image_name'] = self.image_name
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = IMFP
    form_class = IMFPUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = IMFP
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = IMFP
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = IMFP
    attachment = True
    use_unique = True

class PlotView(base.FormView):
    model = IMFP
    template_name = "image/detail_plot.html"
    form_class = IMFPPlotForm
    success_name = 'image:imfp_plot'
    image_name = 'image:imfp_plot_image'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['nclass'].initial = self.kwargs['nclass']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'], 'nclass': self.kwargs['nclass']}
        context['imageurl'] = reverse(self.image_name, kwargs=kwargs)
        context['object'] = self.model.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        self.kwargs['nclass'] = form.cleaned_data['nclass']
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'], 'nclass': self.kwargs['nclass']}
        return reverse(self.success_name, kwargs=kwargs)

class PlotImageView(base.View):
    model = IMFP

    def get(self, request, **kwargs):
        imfp = self.model.objects.get(pk=kwargs['pk'])
        df = imfp.read_csv()
        unit = imfp.upper.upper.get_scaleunit_display()
        length = np.arange(len(df)) * imfp.pixelsize()
        if kwargs['plotid'] == 0:
            title = 'Single_RF'
        else:
            title = 'Double_RF'
        freq = df[title].values
        plt.figure()
        plt.plot(length, freq, '-k')
        plt.xlabel('IMFP ' + title + ' / ' + unit)
        plt.ylabel('Relative Frequency')
        plt.xlim(0, length[kwargs['nclass']])
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class ImageView(base.ImageView):
    model = IMFP

class IMFPSearch(base.Search):
    model = IMFP

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = IMFPSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = IMFP
    serializer_class = IMFPSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = IMFP
    serializer_class =IMFPSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = IMFP
    serializer_class = IMFPSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = IMFP
    serializer_class = IMFPSerializer

class FileAPIView(base_api.FileAPIView):
    model = IMFP
    attachment = True

class IMFPRemote(remote.FileRemote):
    model = IMFP
    add_name = 'image:api_imfp_add'
    list_name = 'image:api_imfp_list'
    retrieve_name = 'image:api_imfp_retrieve'
    update_name = 'image:api_imfp_update'
    delete_name = 'image:api_imfp_delete'
    file_fields_names = [('file', 'image:api_imfp_file')]
    serializer_class = IMFPSerializer

