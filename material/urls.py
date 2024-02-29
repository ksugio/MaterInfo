from django.urls import path
from .views import material, element

app_name = 'material'
urlpatterns = [
    path('<int:pk>/add', material.AddView.as_view(), name='add'),
    path('<int:pk>/import', material.ImportView.as_view(), name='import'),
    path('<int:pk>/list', material.ListView.as_view(), name='list'),
    path('material/<int:pk>', material.DetailView.as_view(), name='detail'),
    path('material/<int:pk>/update', material.UpdateView.as_view(), name='update'),
    path('material/<int:pk>/delete', material.DeleteView.as_view(), name='delete'),
    path('material/<int:pk>/edit_note', material.EditNoteView.as_view(), name='edit_note'),
    path('material/<int:pk>/file', material.FileView.as_view(), name='file'),
    path('material/<int:pk>/element/add', element.AddView.as_view(), name='element_add'),
    path('element/<int:pk>/update', element.UpdateView.as_view(), name='element_update'),
    path('element/<int:pk>/delete', element.DeleteView.as_view(), name='element_delete'),
    # API
    path('api/<int:pk>/add', material.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', material.ListAPIView.as_view(), name='api_list'),
    path('api/material/<int:pk>', material.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/material/<int:pk>/update', material.UpdateAPIView.as_view(), name='api_update'),
    path('api/material/<int:pk>/file', material.FileAPIView.as_view(), name='api_file'),
    path('api/material/<int:pk>/element/add', element.AddAPIView.as_view(), name='api_element_add'),
    path('api/material/<int:pk>/element/list', element.ListAPIView.as_view(), name='api_element_list'),
    path('api/element/<int:pk>', element.RetrieveAPIView.as_view(), name='api_element_retrieve'),
    path('api/element/<int:pk>/update', element.UpdateAPIView.as_view(), name='api_element_update'),
    path('api/element/<int:pk>/delete', element.DeleteAPIView.as_view(), name='api_element_delete'),
]
