from django.urls import reverse
from project.views import base, base_api, remote
from sample.models import Sample
from ..models.design import Design
from ..models.experiment import Experiment
from ..forms import ExperimentAddForm, ExperimentUpdateForm, BayesianForm, AddSampleForm
from ..serializer import ExperimentSerializer
import json

class AddView(base.AddView):
    model = Experiment
    upper = Design
    form_class = ExperimentAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Ex' + base.DateToday()[2:]
        rcan = upper.random_candidate()
        if rcan:
            form.fields['dispcond'].initial = json.dumps(rcan, indent=2)
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.updated_by = self.request.user
        model.set_condition(form.cleaned_data['dispcond'])
        model.set_model_property()
        return super().form_valid(form)

class DOptimalView(base.AddView):
    model = Experiment
    upper = Design
    fields = ('title', 'note')
    template_name = "project/default_add.html"
    title = 'D-Optimal Add'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'DO' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.updated_by = self.request.user
        model.doptimal()
        model.set_model_property()
        return super().form_valid(form)

class BayesianView(base.AddView):
    model = Experiment
    upper = Design
    form_class = BayesianForm
    template_name = "project/default_add.html"
    title = 'Bayesian Add'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'BO' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.updated_by = self.request.user
        model.bayesian(form.cleaned_data['target'],
                       int(form.cleaned_data['acquisition']))
        model.set_model_property()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Experiment
    upper = Design
    template_name = "design/experiment_list.html"
    paginate_by = 1000
    navigation = [['Add', 'design:experiment_add'],
                  ['D-Optimal', 'design:experiment_doptimal'],
                  ['Bayesian', 'design:experiment_bayesian']]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        context['upper'] = upper
        if upper.columns:
            context['columns'] = json.loads(upper.columns).values()
        return context

class UpdateView(base.UpdateView):
    model = Experiment
    form_class = ExperimentUpdateForm
    template_name = "project/default_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['dispcond'].initial = json.dumps(model.get_condition(), indent=2)
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.set_condition(form.cleaned_data['dispcond'])
        return super().form_valid(form)

class DeleteView(base.DeleteView):
    model = Experiment
    template_name = "project/default_delete.html"

class AddSampleView(base.FormView):
    model = Experiment
    form_class = AddSampleForm
    template_name = "project/default_add.html"
    title = 'Experiment Sample Add'
    success_name = 'design:experiment_list'

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = model.title
        form.fields['note'].initial = model.note
        return form

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        upper = model.upper.upper
        Sample.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=upper,
                              title=form.cleaned_data['title'], note=form.cleaned_data['note'],
                              design=model.unique)
        return super().form_valid(form)

    def get_success_url(self):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name, kwargs={'pk': model.upper.id})

class ExperimentSearch(base.Search):
    model = Experiment

# API
class AddAPIView(base_api.AddAPIView):
    upper = Design
    serializer_class = ExperimentSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Design
    model = Experiment
    serializer_class = ExperimentSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Experiment
    serializer_class = ExperimentSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Experiment
    serializer_class = ExperimentSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Experiment
    serializer_class = ExperimentSerializer

class ExperimentRemote(remote.Remote):
    model = Experiment
    add_name = 'design:api_experiment_add'
    list_name = 'design:api_experiment_list'
    retrieve_name = 'design:api_experiment_retrieve'
    update_name = 'design:api_experiment_update'
    delete_name = 'design:api_experiment_delete'
    serializer_class = ExperimentSerializer
    synchronize = True
