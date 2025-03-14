from project.views import base, base_api, remote
from ..models.article import Article
from ..models.clip import Clip
from ..forms import ClipUpdateForm
from ..serializer import ClipSerializer

class AddView(base.AddView):
    model = Clip
    upper = Article
    fields = ('title', 'note', 'start', 'end')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Cl' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.clip_pdf()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Clip
    upper = Article
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:clip_add'],]

class DetailView(base.DetailView):
    model = Clip
    template_name = "reference/clip_detail.html"
    navigation = []

class UpdateView(base.UpdateView):
    model = Clip
    form_class = ClipUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if form.cleaned_data['re_extract']:
            model.clip_pdf()
        return super().form_valid(form)

class DeleteView(base.DeleteManagerView):
    model = Clip
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Clip
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class FileView(base.FileView):
    model = Clip
    attachment = False

class ClipSearch(base.Search):
    model = Clip

# API
class AddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = ClipSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Article
    model = Clip
    serializer_class = ClipSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Clip
    serializer_class = ClipSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Clip
    serializer_class = ClipSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Clip
    serializer_class = ClipSerializer

class FileAPIView(base_api.FileAPIView):
    model = Clip
    attachment = False

class ClipRemote(remote.FileRemote):
    model = Clip
    add_name = 'reference:api_clip_add'
    list_name = 'reference:api_clip_list'
    retrieve_name = 'reference:api_clip_retrieve'
    update_name = 'reference:api_clip_update'
    delete_name = 'reference:api_clip_delete'
    file_fields_names = [('file', 'reference:api_clip_file')]
    serializer_class = ClipSerializer
