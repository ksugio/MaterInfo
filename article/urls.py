from django.urls import path
from .views import article, file, diff

app_name = 'article'
urlpatterns = [
    path('<int:pk>/add', article.AddView.as_view(), name='add'),
    path('<int:pk>/import', article.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', article.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', article.ListView.as_view(), name='list'),
    path('article/<int:pk>', article.DetailView.as_view(), name='detail'),
    path('article/<int:pk>/update', article.UpdateView.as_view(), name='update'),
    path('article/<int:pk>/edit', article.EditView.as_view(), name='edit'),
    path('article/<int:pk>/delete', article.DeleteView.as_view(), name='delete'),
    path('article/<int:pk>/file', article.FileView.as_view(), name='file'),
    path('article/<int:pk>/upload', article.UploadView.as_view(), name='upload'),
    path('article/<int:pk>/download', article.DownloadView.as_view(), name='download'),
    path('article/<int:pk>/download_zip', article.DownloadZipView.as_view(), name='download_zip'),
    path('article/<int:pk>/translate', article.TranslateView.as_view(), name='translate'),
    path('article/<int:pk>/token/<int:ind>', article.TokenView.as_view(), name='token'),
    path('article/<int:pk>/pull', article.PullView.as_view(), name='pull'),
    path('article/<int:pk>/push', article.PushView.as_view(), name='push'),
    path('article/<int:pk>/log', article.LogView.as_view(), name='log'),
    path('article/<int:pk>/set_remote', article.SetRemoteView.as_view(), name='set_remote'),
    path('article/<int:pk>/clear_remote', article.ClearRemoteView.as_view(), name='clear_remote'),
    path('<int:pk>/search', article.SearchView.as_view(), name='search'),
    # API
    path('api/<int:pk>/add', article.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', article.ListAPIView.as_view(), name='api_list'),
    path('api/article/<int:pk>', article.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/article/<int:pk>/update', article.UpdateAPIView.as_view(), name='api_update'),
    path('api/article/<int:pk>/file', article.FileAPIView.as_view(), name='api_file'),
    path('api/article/<int:pk>/pdf', article.PDFAPIView.as_view(), name='api_pdf'),
    # File
    path('article/<int:pk>/file/add', file.FileAddView.as_view(), name='file_add'),
    path('article/<int:pk>/file/list', file.FileListView.as_view(), name='file_list'),
    path('file/<int:pk>/update', file.FileUpdateView.as_view(), name='file_update'),
    path('file/<int:pk>/delete', file.FileDeleteView.as_view(), name='file_delete'),
    path('file/<str:unique>/file', file.FileFileView.as_view(), name='file_file'),
    # File API
    path('api/article/<int:pk>/file/add', file.FileAddAPIView.as_view(), name='api_file_add'),
    path('api/article/<int:pk>/file/list', file.FileListAPIView.as_view(), name='api_file_list'),
    path('api/file/<int:pk>', file.FileRetrieveAPIView.as_view(), name='api_file_retrieve'),
    path('api/file/<int:pk>/update', file.FileUpdateAPIView.as_view(), name='api_file_update'),
    path('api/file/<int:pk>/delete', file.FileDeleteAPIView.as_view(), name='api_file_delete'),
    path('api/file/<int:pk>/file', file.FileFileAPIView.as_view(), name='api_file_file'),
    # Diff
    path('diff/<int:pk>/previous', diff.DiffPreviousView.as_view(), name='diff_previous'),
    path('diff/<int:pk>/diff', diff.DiffDiffView.as_view(), name='diff_diff'),
    path('diff/<int:pk>/restore', diff.DiffRestoreView.as_view(), name='diff_restore'),
    # Diff API
    path('api/article/<int:pk>/diff/add', diff.DiffAddAPIView.as_view(), name='api_diff_add'),
    path('api/article/<int:pk>/diff/list', diff.DiffListAPIView.as_view(), name='api_diff_list'),
    path('api/diff/<int:pk>', diff.DiffRetrieveAPIView.as_view(), name='api_diff_retrieve'),
    path('api/diff/<int:pk>/update', diff.DiffUpdateAPIView.as_view(), name='api_diff_update'),
    path('api/diff/<int:pk>/delete', diff.DiffDeleteAPIView.as_view(), name='api_diff_delete')
]
