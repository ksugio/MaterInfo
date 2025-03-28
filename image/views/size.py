from django.http import HttpResponse
from django.urls import reverse
from project.views import base, base_api, remote, prefix
from ..models.filter import Filter, cv2PIL
from ..models.size import Size
from ..serializer import SizeSerializer
from ..forms import ContoursForm, SizeAddForm, SizeUpdateForm, SizePlotForm
from io import BytesIO
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(prefix.AddPrefixView):
    model = Size
    upper = Filter
    form_class = SizeAddForm
    template_name ="project/default_add.html"
    title_initial = 'Size'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = self.title_initial + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Size
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:size_add'],]

class DetailView(base.DetailView):
    model = Size
    template_name = "image/size_detail.html"
    plot_name = 'image:size_plot'
    file_name = 'image:size_file'
    edit_note_name = 'image:size_edit_note'
    contours_name = 'image:size_contours'
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.results:
            context['results'] = json.loads(model.results)
        context['plot_name'] = self.plot_name
        context['file_name'] = self.file_name
        context['edit_note_name'] = self.edit_note_name
        context['contours_name'] = self.contours_name
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Size
    form_class = SizeUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class EditNoteView(base.MDEditView):
    model = Size
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Size
    template_name = "project/default_delete.html"

class FileView(base.FileView):
    model = Size
    attachment = True
    use_unique = True

class PlotView(base.FormView):
    model = Size
    template_name = "image/detail_plot.html"
    form_class = SizePlotForm
    success_name = 'image:size_plot'
    image_name = 'image:size_plot_image'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
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
    model = Size

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        df = model.read_csv()
        unit = model.upper.upper.get_scaleunit_display()
        plotid = kwargs['plotid']
        bins = kwargs['bins']
        plt.figure()
        if plotid == 0:
            plt.hist(df['Diameter'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('Diameter' + ' / ' + unit)
            plt.ylabel('Frequency')
        elif plotid == 1:
            plt.hist(df['LongSide'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('LongSide' + ' / ' + unit)
            plt.ylabel('Frequency')
        elif plotid == 2:
            plt.hist(df['NarrowSide'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('NarrowSide' + ' / ' + unit)
            plt.ylabel('Frequency')
        elif plotid == 3:
            plt.hist(df['AspectRatio'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('AspectRatio')
            plt.ylabel('Frequency')
        elif plotid == 4:
            plt.hist(df['Circularity'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('Circularity')
            plt.ylabel('Frequency')
        else:
            plt.hist(df['Angle'], bins=bins, color='white', edgecolor='black')
            plt.xlabel('Angle' + ' / degree')
            plt.ylabel('Frequency')
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class ContoursView(base.FormView):
    model = Size
    template_name = "image/detail_plot.html"
    form_class = ContoursForm
    success_name = 'image:size_contours'
    image_name = 'image:size_contours_image'

    def to_bool(self, val):
        if val == 0:
            return False
        else:
            return True

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['gc'].initial = self.to_bool(self.kwargs['gc'])
        form.fields['bb'].initial = self.to_bool(self.kwargs['bb'])
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = {'pk': self.kwargs['pk'], 'gc': self.kwargs['gc'], 'bb': self.kwargs['bb']}
        context['imageurl'] = reverse(self.image_name, kwargs=kwargs)
        context['object'] = self.model.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        self.kwargs['gc'] = int(form.cleaned_data['gc'])
        self.kwargs['bb'] = int(form.cleaned_data['bb'])
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'pk': self.kwargs['pk'], 'gc': self.kwargs['gc'], 'bb': self.kwargs['bb']}
        return reverse(self.success_name, kwargs=kwargs)

class ContoursImageView(base.View):
    model = Size

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        contsimg = model.contsimg(kwargs['gc'], kwargs['bb'])
        if contsimg is None:
            return HttpResponse('Cannot read image file.')
        else:
            pilimg = cv2PIL(contsimg)
            buf = BytesIO()
            pilimg.save(buf, format='png')
            response = HttpResponse(buf.getvalue(), content_type='image/png')
            buf.close()
            return response

# class ContoursJsonView(base.View):
#     model = Size
#
#     def get(self, request, **kwargs):
#         model = self.model.objects.get(pk=kwargs['pk'])
#         data = model.contours_json()
#         response = HttpResponse(data, content_type='application/json')
#         now = datetime.datetime.now()
#         filename = 'Contours%s.json' % (now.strftime('%Y%m%d%H%M%S')[2:])
#         response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
#         return response

class SizeSearch(base.Search):
    model = Size

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = SizeSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Size
    serializer_class = SizeSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Size
    serializer_class =SizeSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Size
    serializer_class = SizeSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Size
    serializer_class = SizeSerializer

class FileAPIView(base_api.FileAPIView):
    model = Size
    attachment = True

class SizeRemote(remote.FileRemote):
    model = Size
    add_name = 'image:api_size_add'
    list_name = 'image:api_size_list'
    retrieve_name = 'image:api_size_retrieve'
    update_name = 'image:api_size_update'
    delete_name = 'image:api_size_delete'
    file_fields_names = [('file', 'image:api_size_file')]
    serializer_class = SizeSerializer
