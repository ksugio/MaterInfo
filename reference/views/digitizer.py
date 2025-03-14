from project.views import base, base_api, remote
from ..models.image import Image
from ..models.digitizer import Digitizer
from ..serializer import DigitizerSerializer
from io import BytesIO
import base64
import json

class AddView(base.AddView):
    model = Digitizer
    upper = Image
    fields = ('title', 'note')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Digi' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Digitizer
    upper = Image
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:digitizer_add'],]

class DetailView(base.DetailView):
    model = Digitizer
    template_name = "reference/digitizer_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.data:
            data = json.loads(model.data)
            if 'axis' in data:
                context['axis'] = data['axis']
        return context

class UpdateView(base.UpdateView):
    model = Digitizer
    fields = ('title', 'note')
    template_name = "project/default_update.html"

class MeasureView(base.TemplateView):
    model = Digitizer
    template_name = "reference/digitizer_measure.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=kwargs['pk'])
        pixmap = model.upper.get_trim_pixmap()
        if pixmap is not None:
            buf = BytesIO(pixmap.pil_tobytes("png"))
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
        else:
            image_base64 = None
        context['object'] = model
        context['pixmap'] = pixmap
        context['image_base64'] = image_base64
        context['server_host'] = self.request._current_scheme_host
        return context

class DeleteView(base.DeleteManagerView):
    model = Digitizer
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Digitizer
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class FileView(base.FileView):
    model = Digitizer
    attachment = True
    use_unique = True

class TableView(base.TableView):
    model = Digitizer

class DigitizerSearch(base.Search):
    model = Digitizer

# API
class AddAPIView(base_api.AddAPIView):
    upper = Image
    serializer_class = DigitizerSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Image
    model = Digitizer
    serializer_class = DigitizerSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Digitizer
    serializer_class = DigitizerSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Digitizer
    serializer_class = DigitizerSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.save_csv()

class DeleteAPIView(base_api.DeleteAPIView):
    model = Digitizer
    serializer_class = DigitizerSerializer

class FileAPIView(base_api.FileAPIView):
    model = Digitizer

class DigitizerRemote(remote.FileRemote):
    model = Digitizer
    add_name = 'reference:api_digitizer_add'
    list_name = 'reference:api_digitizer_list'
    retrieve_name = 'reference:api_digitizer_retrieve'
    update_name = 'reference:api_digitizer_update'
    delete_name = 'reference:api_digitizer_delete'
    file_fields_names = [('file', 'reference:api_digitizer_file')]
    serializer_class = DigitizerSerializer
