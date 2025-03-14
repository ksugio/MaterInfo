from project.views import base, base_api, remote
from ..models import Density, Material
from ..serializer import MaterialSerializer

class AddView(base.AddView):
    model = Material
    upper = Density
    fields = ('name', 'density', 'fraction')
    template_name = "project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Material
    fields = ('name', 'density', 'fraction')
    template_name = "project/default_update.html"
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Material
    template_name = "project/default_delete.html"
    bdcl_remove = 1

# API
class AddAPIView(base_api.AddAPIView):
    upper = Density
    serializer_class = MaterialSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Density
    model = Material
    serializer_class = MaterialSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Material
    serializer_class = MaterialSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Material
    serializer_class = MaterialSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Material
    serializer_class = MaterialSerializer

class MaterialRemote(remote.Remote):
    model = Material
    add_name = 'density:api_material_add'
    list_name = 'density:api_material_list'
    retrieve_name = 'density:api_material_retrieve'
    update_name = 'density:api_material_update'
    delete_name = 'density:api_material_delete'
    serializer_class = MaterialSerializer
    synchronize = True
