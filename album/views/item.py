from project.views import base, base_api, remote
from ..models.album import Album
from ..models.item import Item
from ..forms import ItemForm
from ..serializer import ItemSerializer

class AddView(base.AddView):
    model = Item
    upper = Album
    form_class = ItemForm
    template_name = "project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "album/item_update.html"
    bdcl_remove = 1

    def get_success_url(self):
        return self.object.get_update_url()

class DeleteView(base.DeleteView):
    model = Item
    template_name = 'project/default_delete.html'

class ImageView(base.ImageView):
    model = Item

# API
class AddAPIView(base_api.AddAPIView):
    upper = Album
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Album
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
    add_name = 'album:api_item_add'
    list_name = 'album:api_item_list'
    retrieve_name = 'album:api_item_retrieve'
    update_name = 'album:api_item_update'
    delete_name = 'album:api_item_delete'
    serializer_class = ItemSerializer
    synchronize = True
