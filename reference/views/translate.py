from project.views import base, base_api, remote
from ..models.text import Text
from ..models.translate import Translate
from ..forms import TranslateAddForm, TranslateUpdateForm
from ..serializer import TranslateSerializer

class AddView(base.AddView):
    model = Translate
    upper = Text
    form_class = TranslateAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Trans' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.set_text(form.cleaned_data['api_key'])
        return super().form_valid(form)

class ListView(base.ListView):
    model = Translate
    upper = Text
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:translate_add'],]

class DetailView(base.DetailView):
    model = Translate
    template_name = "reference/translate_detail.html"
    navigation = []

class UpdateView(base.UpdateView):
    model = Translate
    form_class = TranslateUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        if form.cleaned_data['re_extract']:
            model.set_text(form.cleaned_data['api_key'])
        return super().form_valid(form)

class EditView(base.MDEditView):
    model = Translate
    text_field = 'text'
    template_name = "reference/translate_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['image_ids'] = range(model.upper.nimages)
        return context

class DeleteView(base.DeleteManagerView):
    model = Translate
    template_name = "project/default_delete.html"

# API
class AddAPIView(base_api.AddAPIView):
    upper = Text
    serializer_class = TranslateSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Text
    model = Translate
    serializer_class = TranslateSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Translate
    serializer_class = TranslateSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Translate
    serializer_class = TranslateSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Translate
    serializer_class = TranslateSerializer

class TranslateRemote(remote.Remote):
    model = Translate
    add_name = 'reference:api_translate_add'
    list_name = 'reference:api_translate_list'
    retrieve_name = 'reference:api_translate_retrieve'
    update_name = 'reference:api_translate_update'
    delete_name = 'reference:api_translate_delete'
    serializer_class = TranslateSerializer
