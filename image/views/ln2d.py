from django.http import HttpResponse
from django.urls import reverse
from project.views import base, base_api, remote, prefix
from project.forms import EditNoteForm
from plot.views.item import Item
from ..models.filter import Filter
from ..models.ln2d import LN2D
from ..serializer import LN2DSerializer
from ..forms import LN2DPlotForm, LN2DAddForm, LN2DUpdateForm
from io import BytesIO
from random import randint
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(prefix.AddPrefixView):
    model = LN2D
    upper = Filter
    form_class = LN2DAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'LN2D' + base.DateToday()[2:]
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
    model = LN2D
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:ln2d_add'],]

class DetailView(base.DetailView):
    model = LN2D
    template_name = "image/ln2d_detail.html"
    navigation = []

class UpdateView(prefix.UpdatePrefixView):
    model = LN2D
    form_class = LN2DUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if model.file:
            prev = model.file.url
        else:
            prev = 'No File'
        model.measure()
        response = super().form_valid(form)
        items = Item.objects.filter(url=prev)
        for item in items:
            item.url = model.file.url
            item.save()
        return response

class EditNoteView(base.EditNoteView):
    model = LN2D
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = LN2D
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = LN2D
    attachment = True

class PlotView(base.FormView):
    model = LN2D
    template_name = "image/detail_plot.html"
    form_class = LN2DPlotForm
    success_name = 'image:ln2d_plot'
    image_name = 'image:ln2d_plot_image'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['lnmax'].initial = self.kwargs['lnmax']
        if self.kwargs['uniform'] > 0:
            form.fields['uniform'].initial = True
        else:
            form.fields['uniform'].initial = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'],
                  'lnmax': self.kwargs['lnmax'], 'uniform': self.kwargs['uniform']}
        context['imageurl'] = reverse(self.image_name, kwargs=kwargs)
        context['object'] = self.model.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        self.kwargs['lnmax'] = form.cleaned_data['lnmax']
        self.kwargs['uniform'] = int(form.cleaned_data['uniform'])
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'pk': self.kwargs['pk'], 'plotid': self.kwargs['plotid'],
                  'lnmax': self.kwargs['lnmax'], 'uniform': self.kwargs['uniform']}
        return reverse(self.success_name, kwargs=kwargs)

class PlotImageView(base.View):
    model = LN2D

    def get(self, request, **kwargs):
        ln2d = self.model.objects.get(pk=kwargs['pk'])
        df = ln2d.read_csv()
        lnmax = len(df)
        plotid = kwargs['plotid']
        uniform = kwargs['uniform']
        if plotid == 0:
            title = 'LN2D_RF'
            if uniform > 0:
                prob = ln2d.ln2d_prob(lnmax)
            else:
                prob = None
        elif plotid == 1:
            title = 'LN2DR_RF'
            if uniform > 0:
                prob = ln2d.ln2dr_prob(lnmax)
            else:
                prob = None
        else:
            return HttpResponse('Invalid plotid.')
        ln = df['LN'].values
        freq = df[title].values
        plt.figure()
        plt.bar(ln, freq, color='white', edgecolor='black')
        if prob:
            plt.plot(prob[0], prob[1], 'k-', lw=1)
        plt.xlabel(title)
        plt.ylabel('Relative Frequency')
        plt.xlim(-0.5, kwargs['lnmax'])
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class LN2DSearch(base.Search):
    model = LN2D

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = LN2DSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = LN2D
    serializer_class = LN2DSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = LN2D
    serializer_class =LN2DSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = LN2D
    serializer_class = LN2DSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = LN2D
    serializer_class = LN2DSerializer

class FileAPIView(base_api.FileAPIView):
    model = LN2D
    attachment = True

class LN2DRemote(remote.FileRemote):
    model = LN2D
    add_name = 'image:api_ln2d_add'
    list_name = 'image:api_ln2d_list'
    retrieve_name = 'image:api_ln2d_retrieve'
    update_name = 'image:api_ln2d_update'
    delete_name = 'image:api_ln2d_delete'
    file_fields_names = [('file', 'image:api_ln2d_file')]
    serializer_class = LN2DSerializer
