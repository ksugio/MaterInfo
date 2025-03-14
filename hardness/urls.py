from django.urls import path
from .views import hardness, value

app_name = 'hardness'
urlpatterns = [
    path('<int:pk>/add', hardness.AddView.as_view(), name='add'),
    path('<int:pk>/import', hardness.ImportView.as_view(), name='import'),
    path('<int:pk>list', hardness.ListView.as_view(), name='list'),
    path('hardness/<int:pk>', hardness.DetailView.as_view(), name='detail'),
    path('hardness/<int:pk>/update', hardness.UpdateView.as_view(), name='update'),
    path('hardness/<int:pk>/delete', hardness.DeleteView.as_view(), name='delete'),
    path('hardness/<int:pk>/move', hardness.MoveView.as_view(), name='move'),
    path('hardness/<int:pk>/edit_note', hardness.EditNoteView.as_view(), name='edit_note'),
    path('hardness/<int:pk>/value/add', value.AddView.as_view(), name='value_add'),
    path('value/<int:pk>/update', value.UpdateView.as_view(), name='value_update'),
    path('value/<int:pk>/delete', value.DeleteView.as_view(), name='value_delete'),
    # API
    path('api/<int:pk>/add', hardness.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', hardness.ListAPIView.as_view(), name='api_list'),
    path('api/hardness/<int:pk>', hardness.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/hardness/<int:pk>/update', hardness.UpdateAPIView.as_view(), name='api_update'),
    path('api/hardness/<int:pk>/value/add', value.AddAPIView.as_view(), name='api_value_add'),
    path('api/value/<int:pk>/list', value.ListAPIView.as_view(), name='api_value_list'),
    path('api/value/<int:pk>', value.RetrieveAPIView.as_view(), name='api_value_retrieve'),
    path('api/value/<int:pk>/update', value.UpdateAPIView.as_view(), name='api_value_update'),
    path('api/value/<int:pk>/delete', value.DeleteAPIView.as_view(), name='api_value_delete'),
]
