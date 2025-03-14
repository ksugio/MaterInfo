from project.views import base, base_api, remote
from ..models.area import Area
from ..models.item import Item
from ..forms import ItemForm
from ..serializer import ItemSerializer

class AddView(base.AddView):
    model = Item
    upper = Area
    form_class = ItemForm
    template_name = "project/default_add.html"
    bdcl_remove = 2

class UpdateView(base.UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "project/default_update.html"
    bdcl_remove = 2

class DeleteView(base.DeleteView):
    model = Item
    template_name = 'project/default_delete.html'

# API
class AddAPIView(base_api.AddAPIView):
    upper = Area
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Area
    model = Item
    serializer_class = ItemSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Item
    serializer_class = ItemSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Item
    serializer_class = ItemSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Item
    serializer_class = ItemSerializer

class ItemRemote(remote.Remote):
    model = Item
    add_name = None
    list_name = 'plot:api_item_list'
    retrieve_name = None
    update_name = None
    delete_name = 'plot:api_item_delete'
    serializer_class = ItemSerializer
    synchronize = True
