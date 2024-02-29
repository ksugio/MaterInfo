from project.views import base, base_api, remote
from ..models import Hardness, Value
from ..serializer import ValueSerializer

class AddView(base.AddView):
    model = Value
    upper = Hardness
    fields = ('value',)
    template_name = "project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Value
    fields = ('value', 'status')
    template_name = "project/default_update.html"
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Value
    template_name = "project/default_delete.html"
    bdcl_remove = 1

# API
class AddAPIView(base_api.AddAPIView):
    upper = Hardness
    serializer_class = ValueSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Hardness
    model = Value
    serializer_class = ValueSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Value
    serializer_class = ValueSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Value
    serializer_class = ValueSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Value
    serializer_class = ValueSerializer

class ValueRemote(remote.Remote):
    model = Value
    add_name = 'hardness:api_value_add'
    list_name = 'hardness:api_value_list'
    retrieve_name = 'hardness:api_value_retrieve'
    update_name = 'hardness:api_value_update'
    delete_name = 'hardness:api_value_delete'
    serializer_class = ValueSerializer
    synchronize = True
