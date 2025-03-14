from project.views import base, base_api, remote, prefix
from ..models.design import Design
from ..models.condition import Condition
from ..forms import ConditionAddForm, ConditionUpdateForm
from ..serializer import ConditionSerializer

class AddView(prefix.AddPrefixView):
    model = Condition
    upper = Design
    form_class = ConditionAddForm
    template_name = "project/default_add.html"
    disp_default = False
    bdcl_remove = 1

class UpdateView(prefix.UpdatePrefixView):
    model = Condition
    form_class = ConditionUpdateForm
    template_name = "project/default_update.html"
    disp_default = False
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Condition
    template_name = 'project/default_delete.html'
    bdcl_remove = 1

# API
class AddAPIView(base_api.AddAPIView):
    upper = Design
    serializer_class = ConditionSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Design
    model = Condition
    serializer_class = ConditionSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Condition
    serializer_class = ConditionSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Condition
    serializer_class = ConditionSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Condition
    serializer_class = ConditionSerializer

class ConditionRemote(remote.Remote):
    model = Condition
    add_name = 'design:api_condition_add'
    list_name = 'design:api_condition_list'
    retrieve_name = 'design:api_condition_retrieve'
    update_name = 'design:api_condition_update'
    delete_name = 'design:api_condition_delete'
    serializer_class = ConditionSerializer
    synchronize = True
