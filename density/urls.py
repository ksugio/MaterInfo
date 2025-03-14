from django.urls import path
from .views import density, material

app_name = 'density'
urlpatterns = [
    path('<int:pk>/add', density.AddView.as_view(), name='add'),
    path('<int:pk>/import', density.ImportView.as_view(), name='import'),
    path('<int:pk>/list', density.ListView.as_view(), name='list'),
    path('density/<int:pk>', density.DetailView.as_view(), name='detail'),
    path('density/<int:pk>/update', density.UpdateView.as_view(), name='update'),
    path('density/<int:pk>/delete', density.DeleteView.as_view(), name='delete'),
    path('density/<int:pk>/move', density.MoveView.as_view(), name='move'),
    path('density/<int:pk>/edit_note', density.EditNoteView.as_view(), name='edit_note'),
    path('density/<int:pk>/material/add', material.AddView.as_view(), name='material_add'),
    path('material/<int:pk>/update', material.UpdateView.as_view(), name='material_update'),
    path('material/<int:pk>/delete', material.DeleteView.as_view(), name='material_delete'),
    # API
    path('api/<int:pk>/add', density.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', density.ListAPIView.as_view(), name='api_list'),
    path('api/density/<int:pk>', density.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/density/<int:pk>/update', density.UpdateAPIView.as_view(), name='api_update'),
    path('api/density/<int:pk>/material/add', material.AddAPIView.as_view(), name='api_material_add'),
    path('api/density/<int:pk>/material/list', material.ListAPIView.as_view(), name='api_material_list'),
    path('api/material/<int:pk>', material.RetrieveAPIView.as_view(), name='api_material_retrieve'),
    path('api/material/<int:pk>/update', material.UpdateAPIView.as_view(), name='api_material_update'),
    path('api/material/<int:pk>/delete', material.DeleteAPIView.as_view(), name='api_material_delete'),
]
