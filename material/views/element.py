from project.views import base, base_api, remote
from ..models import Material, Element
from ..serializer import ElementSerializer

class AddView(base.AddView):
    model = Element
    upper = Material
    fields = ('element', 'fraction')
    template_name = "project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Element
    fields = ('element', 'fraction')
    template_name = "project/default_update.html"
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Element
    template_name = "project/default_delete.html"
    bdcl_remove = 1

# API
class AddAPIView(base_api.AddAPIView):
    upper = Material
    serializer_class = ElementSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Material
    model = Element
    serializer_class = ElementSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Element
    serializer_class = ElementSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Element
    serializer_class = ElementSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Element
    serializer_class = ElementSerializer

class ElementRemote(remote.Remote):
    model = Element
    add_name = 'material:api_element_add'
    list_name = 'material:api_element_list'
    retrieve_name = 'material:api_element_retrieve'
    update_name = 'material:api_element_update'
    delete_name = 'material:api_element_delete'
    serializer_class = ElementSerializer
    synchronize = True
