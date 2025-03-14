from django.http import HttpResponse
from project.views import base, base_api, remote
from ..models.regression import Regression
from ..models.regrepred import RegrePred
from ..serializer import RegrePredSerializer
import io
import json
import datetime

class AddView(base.AddView):
    model = RegrePred
    upper = Regression
    fields = ('title', 'note', 'file', 'objective', 'drop')
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'RPred' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        response = super().form_valid(form)
        model.predict()
        model.save()
        return response

class ListView(base.ListView):
    model = RegrePred
    upper = Regression
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:regrepred_add'],]

class DetailView(base.DetailView):
    model = RegrePred
    template_name = "collect/regrepred_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.results:
            context['results'] = json.loads(model.results)
        return context

class UpdateView(base.UpdateView):
    model = RegrePred
    fields = ('title', 'status', 'note', 'file', 'objective', 'drop')
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        response = super().form_valid(form)
        model.predict()
        model.save()
        return response

class EditNoteView(base.MDEditView):
    model = RegrePred
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(base.DeleteView):
    model = RegrePred
    template_name = "project/default_delete.html"

class TableView(base.TableView):
    model = RegrePred

class DownloadView(base.View):
    model = RegrePred

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        df = model.disp_table()
        buf = io.StringIO()
        df.to_csv(buf)
        response = HttpResponse(buf.getvalue(), content_type='text/csv; charset=Shift-JIS')
        buf.close()
        now = datetime.datetime.now()
        filename = 'RegrePred_%s.csv' % (now.strftime('%Y%m%d_%H%M%S'))
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        return response

# API
class AddAPIView(base_api.AddAPIView):
    upper = Regression
    serializer_class = RegrePredSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Regression
    model = RegrePred
    serializer_class = RegrePredSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = RegrePred
    serializer_class = RegrePredSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = RegrePred
    serializer_class = RegrePredSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = RegrePred
    serializer_class = RegrePredSerializer

class FileAPIView(base_api.FileAPIView):
    model = RegrePred

class RegrePredRemote(remote.FileRemote):
    model = RegrePred
    add_name = 'collect:api_regrepred_add'
    list_name = 'collect:api_regrepred_list'
    retrieve_name = 'collect:api_regrepred_retrieve'
    update_name = 'collect:api_regrepred_update'
    delete_name = 'collect:api_regrepred_delete'
    file_fields_names = [('file', 'collect:api_regrepred_file')]
    serializer_class = RegrePredSerializer
