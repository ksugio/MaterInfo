from django.forms import HiddenInput
from project.views import base, base_api, remote
from ..models import Article, File
from ..forms import FileAddForm, FileUpdateForm
from ..serializer import FileSerializer

class FileAddView(base.AddView):
    model = File
    upper = Article
    form_class = FileAddForm
    template_name = "project/default_add.html"
    bdcl_remove = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        if upper.type == 0:
            form.fields['svg2pdf'].widget = HiddenInput()
        return form

class FileListView(base.ListView):
    model = File
    upper = Article
    template_name = "article/file_list.html"
    title = 'Article File'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upper'] = self.upper.objects.get(pk=self.kwargs['pk'])
        context['breadcrumb_list'] = context['breadcrumb_list'][:-1]
        return context

class FileUpdateView(base.UpdateView):
    model = File
    form_class = FileUpdateForm
    template_name = "project/default_update.html"
    bdcl_remove = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.upper.type == 0:
            form.fields['svg2pdf'].widget = HiddenInput()
        return form

class FileDeleteView(base.DeleteView):
    model = File
    template_name = "project/default_delete.html"
    bdcl_remove = 1

class FileFileView(base.FileView):
    model = File
    attachment = False
    use_unique = True

# API
class FileAddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class FileListAPIView(base_api.ListAPIView):
    upper = Article
    model = File
    serializer_class = FileSerializer

class FileRetrieveAPIView(base_api.RetrieveAPIView):
    model = File
    serializer_class = FileSerializer

class FileUpdateAPIView(base_api.UpdateAPIView):
    model = File
    serializer_class = FileSerializer

class FileDeleteAPIView(base_api.DeleteAPIView):
    model = File
    serializer_class = FileSerializer

class FileFileAPIView(base_api.FileAPIView):
    model = File
    attachment = False

class FileRemote(remote.FileRemote):
    model = File
    add_name = 'article:api_file_add'
    list_name = 'article:api_file_list'
    retrieve_name = 'article:api_file_retrieve'
    update_name = 'article:api_file_update'
    delete_name = 'article:api_file_delete'
    file_fields_names = [('file', 'article:api_file_file')]
    serializer_class = FileSerializer
