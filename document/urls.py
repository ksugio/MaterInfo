from django.urls import path
from . import views

app_name = 'document'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/import', views.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', views.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('document/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('document/<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('document/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('document/<int:pk>/edit_note', views.EditNoteView.as_view(), name='edit_note'),
    path('document/<int:pk>/token/<int:ind>', views.TokenView.as_view(), name='token'),
    path('document/<int:pk>/pull', views.PullView.as_view(), name='pull'),
    path('document/<int:pk>/push', views.PushView.as_view(), name='push'),
    path('document/<int:pk>/set_remote', views.SetRemoteView.as_view(), name='set_remote'),
    path('document/<int:pk>/clear_remote', views.ClearRemoteView.as_view(), name='clear_remote'),
    path('document/<int:pk>/file/add', views.FileAddView.as_view(), name='file_add'),
    path('file/<int:pk>/update', views.FileUpdateView.as_view(), name='file_update'),
    path('file/<int:pk>/file', views.FileView.as_view(), name='file'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/document/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/document/<int:pk>/update', views.UpdateAPIView.as_view(), name='api_update'),
    path('api/document/<int:pk>/file/add', views.FileAddAPIView.as_view(), name='api_file_add'),
    path('api/document/<int:pk>/file/list', views.FileListAPIView.as_view(), name='api_file_list'),
    path('api/file/<int:pk>', views.FileRetrieveAPIView.as_view(), name='api_file_retrieve'),
    path('api/file/<int:pk>/file', views.FileFileAPIView.as_view(), name='api_file_file'),
]
