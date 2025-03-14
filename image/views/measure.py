from django.http import HttpResponse
from project.views import base, base_api, remote, prefix
from ..models.measure import Measure
from ..models.image import Image
from ..models.filter import cv2PIL
from ..forms import MeasureAddForm, MeasureUpdateForm
from ..serializer import MeasureSerializer
from io import BytesIO
import pandas as pd
import base64
import datetime

class AddView(prefix.AddPrefixView):
    model = Measure
    upper = Image
    form_class = MeasureAddForm
    template_name = "project/default_add.html"
    title_initial = 'Meas'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = self.title_initial + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Measure
    upper = Image
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:measure_add'],]

class DetailView(base.DetailView):
    model = Measure
    template_name = "image/measure_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['describe'] = model.get_desc()
        return context

class UpdateView(prefix.UpdatePrefixView):
    model = Measure
    form_class = MeasureUpdateForm
    template_name = "project/default_update.html"

class EditNoteView(base.MDEditView):
    model = Measure
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = Measure
    template_name = "project/default_delete.html"

class MeasureView(base.TemplateView):
    model = Measure
    template_name = "image/measure_measure.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=kwargs['pk'])
        orgimg = model.upper.read_img()
        pilimg = cv2PIL(orgimg)
        buf = BytesIO()
        pilimg.save(buf, format='png')
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        context['object'] = model
        context['pilimg'] = pilimg
        context['image_base64'] = image_base64
        context['server_host'] = self.request._current_scheme_host
        return context

class DownloadView(base.View):
    model = Measure

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        df = model.get_df()
        if df is None:
            df = pd.DataFrame()
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        response = HttpResponse(buf.getvalue(), content_type='text/csv; charset=Shift-JIS')
        buf.close()
        now = datetime.datetime.now()
        filename = 'Measure%s.csv' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

class MeasureSearch(base.Search):
    model = Measure

# API
class AddAPIView(base_api.AddAPIView):
    upper = Image
    serializer_class = MeasureSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Image
    model = Measure
    serializer_class = MeasureSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Measure
    serializer_class =MeasureSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Measure
    serializer_class = MeasureSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Measure
    serializer_class = MeasureSerializer

class MeasureRemote(remote.Remote):
    model = Measure
    add_name = 'image:api_measure_add'
    list_name = 'image:api_measure_list'
    retrieve_name = 'image:api_measure_retrieve'
    update_name = 'image:api_measure_update'
    delete_name = 'image:api_measure_delete'
    serializer_class = MeasureSerializer
