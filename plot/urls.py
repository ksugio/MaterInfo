from django.urls import path
from .views import plot
from .views import area
from .views import item

app_name = 'plot'
urlpatterns = [
    # Plot
    path('<int:pk>/add', plot.AddView.as_view(), name='add'),
    path('<int:pk>/import', plot.ImportView.as_view(), name='import'),
    path('<int:pk>/list', plot.ListView.as_view(), name='list'),
    path('plot/<int:pk>', plot.DetailView.as_view(), name='detail'),
    path('plot/<int:pk>/update', plot.UpdateView.as_view(), name='update'),
    path('plot/<int:pk>/edit_note', plot.EditNoteView.as_view(), name='edit_note'),
    path('plot/<int:pk>/delete', plot.DeleteView.as_view(), name='delete'),
    path('plot/<int:pk>/plot', plot.PlotView.as_view(), name='plot'),
    # Plot API
    path('api/<int:pk>/add', plot.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', plot.ListAPIView.as_view(), name='api_list'),
    path('api/plot/<int:pk>', plot.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/plot/<int:pk>/update', plot.UpdateAPIView.as_view(), name='api_update'),
    path('api/plot/<int:pk>/delete', plot.DeleteAPIView.as_view(), name='api_delete'),
    # Area
    path('plot/<int:pk>/area/add', area.AddView.as_view(), name='area_add'),
    path('area/<int:pk>/update', area.UpdateView.as_view(), name='area_update'),
    path('area/<int:pk>/delete', area.DeleteView.as_view(), name='area_delete'),
    path('area/<int:pk>/plot', area.PlotView.as_view(), name='area_plot'),
    # Area API
    path('api/plot/<int:pk>/area/add', area.AddAPIView.as_view(), name='api_area_add'),
    path('api/plot/<int:pk>/area/list', area.ListAPIView.as_view(), name='api_area_list'),
    path('api/area/<int:pk>', area.RetrieveAPIView.as_view(), name='api_area_retrieve'),
    path('api/area/<int:pk>/update', area.UpdateAPIView.as_view(), name='api_area_update'),
    path('api/area/<int:pk>/delete', area.DeleteAPIView.as_view(), name='api_area_delete'),
    # Item
    path('area/<int:pk>/item/add', item.AddView.as_view(), name='item_add'),
    path('item/<int:pk>/update', item.UpdateView.as_view(), name='item_update'),
    path('item/<int:pk>/delete', item.DeleteView.as_view(), name='item_delete'),
    # Item API
    path('api/area/<int:pk>/item/add', item.AddAPIView.as_view(), name='api_item_add'),
    path('api/area/<int:pk>/item/list', item.ListAPIView.as_view(), name='api_item_list'),
    path('api/item/<int:pk>', item.RetrieveAPIView.as_view(), name='api_item_retrieve'),
    path('api/item/<int:pk>/update', item.UpdateAPIView.as_view(), name='api_item_update'),
    path('api/item/<int:pk>/delete', item.DeleteAPIView.as_view(), name='api_item_delete'),
]
