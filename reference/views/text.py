from django.http import HttpResponse
from project.views import base, base_api, remote
from ..models.article import Article
from ..models.text import Text
from ..forms import TextUpdateForm
from ..serializer import TextSerializer
from .translate import TranslateRemote
from io import BytesIO
import json

class AddView(base.AddView):
    model = Text
    upper = Article
    fields = ('title', 'note', 'start', 'end')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Txt' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.set_text()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Text
    upper = Article
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:text_add'],]

class DetailView(base.DetailView):
    model = Text
    template_name = "reference/text_detail.html"
    navigation = [['Translate', 'reference:translate_list'],]

class UpdateView(base.UpdateView):
    model = Text
    form_class = TextUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if form.cleaned_data['re_extract']:
            model.set_text()
        return super().form_valid(form)

class EditView(base.MDEditView):
    model = Text
    text_field = 'text'
    template_name = "reference/text_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['image_ids'] = range(model.nimages)
        context['tables'] = json.loads(model.tables)
        return context

class DeleteView(base.DeleteManagerView):
    model = Text
    template_name = "project/default_delete.html"

class ImageView(base.View):
    model = Text

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        pixmap = model.extract_pixmap(kwargs['iid'])
        if pixmap is not None:
            buf = BytesIO(pixmap.pil_tobytes("png"))
            response = HttpResponse(buf.getvalue(), content_type='image/png')
            buf.close()
        else:
            response = HttpResponse('Cannot get image.')
        return response

class ThumbnailView(base.View):
    model = Text

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        pixmap = model.extract_pixmap(kwargs['iid'])
        if pixmap is not None:
            pixmap.shrink(kwargs['shrink'])
            buf = BytesIO(pixmap.pil_tobytes("png"))
            response = HttpResponse(buf.getvalue(), content_type='image/png')
            buf.close()
        else:
            response = HttpResponse('Cannot get image.')
        return response

class TextSearch(base.Search):
    model = Text

# API
class AddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = TextSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Article
    model = Text
    serializer_class = TextSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Text
    serializer_class = TextSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Text
    serializer_class = TextSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Text
    serializer_class = TextSerializer

class TextRemote(remote.Remote):
    model = Text
    add_name = 'reference:api_text_add'
    list_name = 'reference:api_text_list'
    retrieve_name = 'reference:api_text_retrieve'
    update_name = 'reference:api_text_update'
    delete_name = 'reference:api_text_delete'
    serializer_class = TextSerializer
    lower_remote = [TranslateRemote]
