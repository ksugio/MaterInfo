from django.shortcuts import render
from project.views import base, base_api, remote, task
from ..models.filter import Filter
from ..models.regression import Regression
from ..models.inverse import Inverse
from ..forms import InverseAddForm, InverseUpdateForm
from ..tasks import InverseTask
from ..serializer import InverseSerializer
import pandas as pd

def GetCandidate(filter):
    regs = Regression.objects.filter(upper=filter).filter(status=0)
    candidate = [('', 'None')]
    for reg in regs:
        candidate.append((reg.unique, reg.title))
    return candidate

class AddView(task.AddView):
    model = Inverse
    upper = Filter
    form_class = InverseAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Inv' + base.DateToday()[2:]
        form.fields['regression1'].choices = GetCandidate(upper)[1:]
        form.fields['regression2'].choices = GetCandidate(upper)
        form.fields['regression3'].choices = GetCandidate(upper)
        return form

    def start_task(self, form, model):
        regdata, suggests = model.regression_data()
        if regdata is not None:
            model.task_id = InverseTask.delay(
                regdata, suggests, model.seed, model.ntrials,
                request_user_id=self.request.user.id
            )

class ListView(base.ListView):
    model = Inverse
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'collect:inverse_add'],]

class DetailView(task.DetailView):
    model = Inverse
    template_name = "collect/inverse_detail.html"
    result_fields = ('file',)

class UpdateView(task.UpdateView):
    model = Inverse
    form_class = InverseUpdateForm
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['regression1'].choices = GetCandidate(model.upper)[1:]
        form.fields['regression1'].initial = model.regression1
        form.fields['regression2'].choices = GetCandidate(model.upper)
        form.fields['regression2'].initial = model.regression2
        form.fields['regression3'].choices = GetCandidate(model.upper)
        form.fields['regression3'].initial = model.regression3
        return form

    def start_task(self, form, model):
        if form.cleaned_data['optimize']:
            regdata, suggests = model.regression_data()
            if regdata is not None:
                model.task_id = InverseTask.delay(
                    regdata, suggests, model.seed, model.ntrials,
                    request_user_id=self.request.user.id
                )
                if model.file:
                    model.file.delete()

class EditNoteView(base.MDEditView):
    model = Inverse
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class DeleteView(task.DeleteView):
    model = Inverse
    template_name = "project/default_delete.html"

class RevokeView(task.RevokeView):
    model = Inverse
    template_name = "project/default_revoke.html"
    success_name = 'collect:inverse_detail'

class FileView(base.FileView):
    model = Inverse
    attachment = True
    use_unique = True

class TableView(base.TableView):
    model = Inverse

class PlotView(base.PlotView):
    model = Inverse

class InverseSearch(base.Search):
    model = Inverse

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = InverseSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Inverse
    serializer_class = InverseSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Inverse
    serializer_class = InverseSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Inverse
    serializer_class = InverseSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Inverse
    serializer_class = InverseSerializer

class FileAPIView(base_api.FileAPIView):
    model = Inverse

class InverseRemote(remote.FileRemote):
    model = Inverse
    add_name = 'collect:api_inverse_add'
    list_name = 'collect:api_inverse_list'
    retrieve_name = 'collect:api_inverse_retrieve'
    update_name = 'collect:api_inverse_update'
    delete_name = 'collect:api_inverse_delete'
    file_fields_names = [('file', 'collect:api_inverse_file')]
    serializer_class = InverseSerializer
