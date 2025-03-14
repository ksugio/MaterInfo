from django.urls import path
from . import views

app_name = 'sample'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/import', views.ImportView.as_view(), name='import'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('<int:pk>/search', views.SearchView.as_view(), name='search'),
    path('sample/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('sample/<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('sample/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('sample/<int:pk>/edit_note', views.EditNoteView.as_view(), name='edit_note'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/sample/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/sample/<int:pk>/update', views.UpdateAPIView.as_view(), name='api_update'),
]
