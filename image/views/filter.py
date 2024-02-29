from django.http import HttpResponse
from django.forms import HiddenInput
from rest_framework import views, status, response
from config.settings import IMAGE_FILTER_LOWER, IMAGE_FILTER_PROCESS
from project.views import base, base_api, remote
from project.forms import AliasForm, EditNoteForm, ImportForm
from album.models.item import Item
from ..models.image import Image
from ..models.filter import Filter, cv2PIL
from ..models.process import Process
from ..serializer import FilterSerializer, FilterAliasSerializer
from .process_api import ProcessRemote
from io import BytesIO
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(base.AddView):
    model = Filter
    upper = Image
    fields = ('title', 'note', 'template', 'format')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Fil' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.savefile()
        return super().form_valid(form)

class AliasView(base.FormView):
    model = Filter
    upper = Image
    form_class = AliasForm
    template_name = "project/default_add.html"
    title = 'Filter Alias'
    success_name = 'image:filter_list'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        models = self.model.objects.filter(template=True).filter(upper__upper__upper=upper.upper.upper)
        candidate = []
        for model in models:
            title = '%s/%s/%s' % (model.upper.upper.title, model.upper.title, model.title)
            candidate.append((model.id, title))
        form.fields['template'].choices = candidate
        return form

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        id = form.cleaned_data['template']
        source = self.model.objects.get(id=id)
        title = source.title + ' (Alias)'
        object = self.model.objects.create(
            created_by=self.request.user, updated_by=self.request.user, upper=upper,
            title=title, alias=source.id)
        object.savefile()
        object.save()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Filter
    upper = Image
    template_name = "project/default_list.html"
    navigation = [['Add', 'image:filter_add'],
                  ['Alias', 'image:filter_alias'],
                  ['Import', 'image:filter_import']]

class DetailView(base.DetailView):
    model = Filter
    template_name = "image/filter_detail.html"

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in IMAGE_FILTER_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        return super().get_context_data(**kwargs)

class UpdateView(base.UpdateView):
    model = Filter
    fields = ('title', 'status', 'note', 'template', 'format')
    template_name = "image/filter_update.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.alias:
            form.fields['template'].widget = HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        processes = Process.objects.filter(upper=model).order_by('order')
        context['process'] = base.Entity(processes)
        add_name = []
        for item in IMAGE_FILTER_PROCESS:
            if 'AddName' in item:
                add_name.append(item['AddName'])
        context['process_add'] = base.NavigationList(add_name, model.id)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if model.file:
            prev = model.file.url
        else:
            prev = 'No File'
        model.savefile()
        response = super().form_valid(form)
        items = Item.objects.filter(url=prev)
        for item in items:
            item.url = model.file.url
            item.save()
        return response

class EditNoteView(base.EditNoteView):
    model = Filter
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteAliasView):
    model = Filter
    template_name = "project/default_delete_alias.html"

class FileView(base.FileView):
    model = Filter
    attachment = False

class ImageView(base.View):
    model = Filter

    def get(self, request, **kwargs):
        filter = self.model.objects.get(pk=kwargs['pk'])
        procid = kwargs['procid']
        img = filter.upper.read_img()
        if img is None:
            return HttpResponse('Cannot read image file.')
        img, kwargs = filter.procimg(img, procid)
        pilimg = cv2PIL(img)
        buf = BytesIO()
        pilimg.save(buf, format='png')
        response = HttpResponse(buf.getvalue(), content_type='image/png')
        buf.close()
        return response

class HistgramView(base.View):
    model = Filter

    def get(self, request, **kwargs):
        filter = self.model.objects.get(pk=kwargs['pk'])
        procid = kwargs['procid']
        img = filter.upper.read_img()
        if img is None:
            return HttpResponse('Cannot read image file.')
        img, kwargs = filter.procimg(img, procid)
        plt.figure()
        lv = range(256)
        if len(img.shape) == 2:
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            plt.plot(lv, hist, 'k')
        elif len(img.shape) == 3:
            col = ['b', 'g', 'r']
            for i in range(3):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                plt.plot(lv, hist, col[i])
        plt.xlabel('Gray Levels')
        plt.ylabel('Number of Pixels')
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class FilterSearch(base.Search):
    model = Filter
    lower_items = IMAGE_FILTER_LOWER

# API
class AddAPIView(base_api.AddAPIView):
    upper = Image
    serializer_class = FilterSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Image
    model = Filter
    serializer_class = FilterSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Filter
    serializer_class = FilterSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Filter
    serializer_class = FilterSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Filter
    serializer_class = FilterSerializer

class FileAPIView(base_api.FileAPIView):
    model = Filter

class AliasAPIView(views.APIView):
    permission_classes = (base_api.IsAuthenticated, base_api.IsMemberUp)
    upper = Image
    model = Filter

    def get(self, request, *args, **kwargs):
        upper = self.upper.objects.get(pk=kwargs['pk'])
        models = self.model.objects.filter(template=True).filter(upper__upper__upper=upper.upper.upper)
        serializer = FilterSerializer(models, many=True)
        return response.Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        upper = self.upper.objects.get(pk=kwargs['pk'])
        serializer = FilterAliasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        object = serializer.save(user=request.user, upper=upper)
        filter = FilterSerializer(object)
        return response.Response(filter.data, status.HTTP_201_CREATED)

class FilterRemote(remote.FileRemote):
    model = Filter
    add_name = 'image:api_filter_add'
    list_name = 'image:api_filter_list'
    retrieve_name = 'image:api_filter_retrieve'
    update_name = 'image:api_filter_update'
    delete_name = 'image:api_filter_delete'
    file_fields_names = [('file', 'image:api_filter_file')]
    serializer_class = FilterSerializer
    child_remote = [ProcessRemote]
    lower_items = IMAGE_FILTER_LOWER

    def create(self, data, upper, user, **kwargs):
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.filter(upper__upper__upper=upper.upper.upper).filter(remoteid=data['alias'])
            if source:
                data['alias'] = source[0].id
            else:
                data['alias'] = None
        return super().create(data, upper, user, **kwargs)

    def update(self, model, data, user, **kwargs):
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.filter(upper__upper__upper=model.upper.upper.upper).filter(remoteid=data['alias'])
            if source:
                data['alias'] = source[0].id
            else:
                data['alias'] = None
        return super().update(model, data, user, **kwargs)

    def data_files(self, model, data, files, **kwargs):
        model, data, files, kwargs = super().data_files(model, data, files, **kwargs)
        if 'alias' in data and data['alias'] is not None:
            source = self.model.objects.get(id=data['alias'])
            data['alias'] = source.remoteid
        return model, data, files, kwargs

class ImportView(remote.ImportView):
    model = Filter
    upper = Image
    form_class = ImportForm
    remote_class = FilterRemote
    template_name = "project/default_import.html"
    title = 'Filter Import'
    success_name = 'image:filter_list'
    view_name = 'image:filter_detail'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.objects is not None:
            model = self.objects[0]
            model.savefile()
            model.save()
        return response
