from django.http import HttpResponse
from rest_framework.response import Response
from project.views import base, base_api, remote
from ..models.article import Article
from ..models.image import Image
from ..serializer import ImageSerializer
from .digitizer import DigitizerRemote
from io import BytesIO
import base64

class AddView(base.AddView):
    model = Image
    upper = Article
    fields = ('title', 'note', 'page', 'scale', 'rotate',
              'startx', 'starty', 'endx', 'endy', 'zoom')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Img' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Image
    upper = Article
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:image_add'],]

class DetailView(base.DetailView):
    model = Image
    template_name = "reference/image_detail.html"
    navigation = [['Digitizer', 'reference:digitizer_list'],]

class UpdateView(base.UpdateView):
    model = Image
    fields = ('title', 'note', 'page', 'scale', 'rotate',
              'startx', 'starty', 'endx', 'endy', 'zoom')
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Image
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Image
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class TrimView(base.TemplateView):
    model = Image
    template_name = "reference/image_trim.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=kwargs['pk'])
        pixmap = model.get_pixmap(model.page, model.scale, model.rotate)
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

class ImageView(base.View):
    model = Image

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        pixmap = model.get_trim_pixmap()
        if pixmap is not None:
            buf = BytesIO(pixmap.pil_tobytes("png"))
            response = HttpResponse(buf.getvalue(), content_type='image/png')
            buf.close()
        else:
            response = HttpResponse('Cannot get image.')
        return response

class ImageSearch(base.Search):
    lower_items = [{'Search': 'reference.views.digitizer.DigitizerSearch'},]
    model = Image

# API
class AddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = ImageSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Article
    model = Image
    serializer_class = ImageSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Image
    serializer_class = ImageSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Image
    serializer_class = ImageSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Image
    serializer_class = ImageSerializer

class PDFImageAPIView(base_api.APIView):
    model = Image

    def get(self, request, pk):
        model = self.model.objects.get(pk=pk)
        return Response({
            'page': model.page,
            'scale': model.scale,
            'rotate': model.rotate
        })

    def post(self, request, pk):
        model = self.model.objects.get(pk=pk)
        page = request.data['page']
        scale = request.data['scale']
        rotate = request.data['rotate']
        pixmap = model.get_pixmap(page, scale, rotate)
        if pixmap is not None:
            buf = BytesIO(pixmap.pil_tobytes("png"))
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            return Response({
                'width': pixmap.width,
                'height': pixmap.height,
                'image': image_base64
            })
        else:
            return Response({
                'width': 0,
                'height': 0,
                'image': None
            })

class ImageRemote(remote.Remote):
    model = Image
    add_name = 'reference:api_image_add'
    list_name = 'reference:api_image_list'
    retrieve_name = 'reference:api_image_retrieve'
    update_name = 'reference:api_image_update'
    delete_name = 'reference:api_image_delete'
    serializer_class = ImageSerializer
    lower_remote = [DigitizerRemote]
