from django.urls import path
from . import views

app_name = 'article'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/import', views.ImportView.as_view(), name='import'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('article/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('article/<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('article/<int:pk>/edit', views.EditView.as_view(), name='edit'),
    path('article/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('article/<int:pk>/upload', views.UploadView.as_view(), name='upload'),
    path('article/<int:pk>/download', views.DownloadView.as_view(), name='download'),
    path('article/<int:pk>/file/add', views.FileAddView.as_view(), name='file_add'),
    path('file/<int:pk>/update', views.FileUpdateView.as_view(), name='file_update'),
    path('file/<int:pk>/delete', views.FileDeleteView.as_view(), name='file_delete'),
    path('file/<str:unique>/file', views.FileFileView.as_view(), name='file_file'),
    path('diff/<int:pk>/previous', views.DiffPreviousView.as_view(), name='diff_previous'),
    path('diff/<int:pk>/diff', views.DiffDiffView.as_view(), name='diff_diff'),
    path('diff/<int:pk>/restore', views.DiffRestoreView.as_view(), name='diff_restore'),
    path('<int:pk>/search', views.SearchView.as_view(), name='search'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/article/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/article/<int:pk>/update', views.UpdateAPIView.as_view(), name='api_update'),
    path('api/article/<int:pk>/file/add', views.FileAddAPIView.as_view(), name='api_file_add'),
    path('api/article/<int:pk>/file/list', views.FileListAPIView.as_view(), name='api_file_list'),
    path('api/file/<int:pk>', views.FileRetrieveAPIView.as_view(), name='api_file_retrieve'),
    path('api/file/<int:pk>/update', views.FileUpdateAPIView.as_view(), name='api_file_update'),
    path('api/file/<int:pk>/delete', views.FileDeleteAPIView.as_view(), name='api_file_delete'),
    path('api/file/<int:pk>/file', views.FileFileAPIView.as_view(), name='api_file_file'),
    path('api/article/<int:pk>/diff/add', views.DiffAddAPIView.as_view(), name='api_diff_add'),
    path('api/article/<int:pk>/diff/list', views.DiffListAPIView.as_view(), name='api_diff_list'),
    path('api/diff/<int:pk>', views.DiffRetrieveAPIView.as_view(), name='api_diff_retrieve'),
    path('api/diff/<int:pk>/update', views.DiffUpdateAPIView.as_view(), name='api_diff_update'),
    path('api/diff/<int:pk>/delete', views.DiffDeleteAPIView.as_view(), name='api_diff_delete'),
]
