from project.views import base, base_api, remote, prefix
from project.forms import EditNoteForm
from ..models.filter import Filter
from ..models.aggregate import Aggregate
from ..forms import AggregateAddForm, AggregateUpdateForm
from ..serializer import AggregateSerializer

class AddView(prefix.AddPrefixView):
    model = Aggregate
    upper = Filter
    form_class = AggregateAddForm
    template_name ="project/default_add.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Agg' + base.DateToday()[2:]
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class ListView(base.ListView):
    model = Aggregate
    upper = Filter
    template_name = "project/default_list.html"
    navigation = [['Add', 'value:aggregate_add'],]

class DetailView(base.DetailView):
    model = Aggregate
    template_name = "value/aggregate_detail.html"
    navigation = []

class UpdateView(prefix.UpdatePrefixView):
    model = Aggregate
    form_class = AggregateUpdateForm
    template_name = "project/default_update.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        model.measure()
        return super().form_valid(form)

class EditNoteView(base.EditNoteView):
    model = Aggregate
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class DeleteView(base.DeleteView):
    model = Aggregate
    template_name = "project/default_delete.html"

class AggregateSearch(base.Search):
    model = Aggregate

# API
class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = AggregateSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = Aggregate
    serializer_class = AggregateSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Aggregate
    serializer_class = AggregateSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Aggregate
    serializer_class = AggregateSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Aggregate
    serializer_class = AggregateSerializer

class AggregateRemote(remote.Remote):
    model = Aggregate
    add_name = 'value:api_aggregate_add'
    list_name = 'value:api_aggregate_list'
    retrieve_name = 'value:api_aggregate_retrieve'
    update_name = 'value:api_aggregate_update'
    delete_name = 'value:api_aggregate_delete'
    serializer_class = AggregateSerializer
