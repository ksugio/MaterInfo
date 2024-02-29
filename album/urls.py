from django.urls import path
from .views import album, item

app_name = 'album'
urlpatterns = [
    path('<int:pk>/add', album.AddView.as_view(), name='add'),
    path('<int:pk>/list', album.ListView.as_view(), name='list'),
    path('album/<int:pk>', album.DetailView.as_view(), name='detail'),
    path('album/<int:pk>/update', album.UpdateView.as_view(), name='update'),
    path('album/<int:pk>/edit_note', album.EditNoteView.as_view(), name='edit_note'),
    path('album/<int:pk>/delete', album.DeleteView.as_view(), name='delete'),
    path('album/<int:pk>/file', album.FileView.as_view(), name='file'),
    # API
    path('api/<int:pk>/add', album.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', album.ListAPIView.as_view(), name='api_list'),
    path('api/album/<int:pk>', album.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/album/<int:pk>/update', album.UpdateAPIView.as_view(), name='api_update'),
    path('api/album/<int:pk>/delete', album.DeleteAPIView.as_view(), name='api_delete'),
    path('api/album/<int:pk>/file', album.FileAPIView.as_view(), name='api_file'),
    # Item
    path('album/<int:pk>/item/add', item.AddView.as_view(), name='item_add'),
    path('item/<int:pk>/update', item.UpdateView.as_view(), name='item_update'),
    path('item/<int:pk>/delete', item.DeleteView.as_view(), name='item_delete'),
    path('item/<int:pk>/image', item.ImageView.as_view(), name='item_image'),
    # Item API
    path('api/album/<int:pk>/item/add', item.AddAPIView.as_view(), name='api_item_add'),
    path('api/album/<int:pk>/item/list', item.ListAPIView.as_view(), name='api_item_list'),
    path('api/item/<int:pk>', item.RetrieveAPIView.as_view(), name='api_item_retrieve'),
    path('api/item/<int:pk>/update', item.UpdateAPIView.as_view(), name='api_item_update'),
    path('api/item/<int:pk>/delete', item.DeleteAPIView.as_view(), name='api_item_delete'),
]
