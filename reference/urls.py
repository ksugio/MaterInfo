from django.urls import path
from .views import reference, article

app_name = 'reference'
urlpatterns = [
    path('<int:pk>/add', reference.AddView.as_view(), name='add'),
    path('<int:pk>/import', reference.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', reference.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', reference.ListView.as_view(), name='list'),
    path('reference/<int:pk>', reference.DetailView.as_view(), name='detail'),
    path('reference/<int:pk>/update', reference.UpdateView.as_view(), name='update'),
    path('reference/<int:pk>/edit_note', reference.EditNoteView.as_view(), name='edit_note'),
    path('reference/<int:pk>/delete', reference.DeleteView.as_view(), name='delete'),
    path('reference/<int:pk>/token/<int:ind>', reference.TokenView.as_view(), name='token'),
    path('reference/<int:pk>/pull', reference.PullView.as_view(), name='pull'),
    path('reference/<int:pk>/push', reference.PushView.as_view(), name='push'),
    path('reference/<int:pk>/set_remote', reference.SetRemoteView.as_view(), name='set_remote'),
    path('reference/<int:pk>/clear_remote', reference.ClearRemoteView.as_view(), name='clear_remote'),
    path('<int:pk>/search', reference.SearchView.as_view(), name='search'),
    # API
    path('api/<int:pk>/add', reference.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', reference.ListAPIView.as_view(), name='api_list'),
    path('api/reference/<int:pk>', reference.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/reference/<int:pk>/update', reference.UpdateAPIView.as_view(), name='api_update'),
    # Article
    path('reference/<int:pk>/article/add', article.AddView.as_view(), name='article_add'),
    path('reference/<int:pk>/article/import', article.ImportView.as_view(), name='article_import'),
    path('reference/<int:pk>/upload', article.UploadView.as_view(), name='article_upload'),
    path('reference/<int:pk>/download', article.DownloadView.as_view(), name='article_download'),
    path('reference/<int:pk>/article/list', article.ListView.as_view(), name='article_list'),
    path('article/<int:pk>', article.DetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/update', article.UpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/edit_note', article.EditNoteView.as_view(), name='article_edit_note'),
    path('article/<int:pk>/delete', article.DeleteView.as_view(), name='article_delete'),
    path('article/<int:pk>/file', article.FileView.as_view(), name='article_file'),
    # Article API
    path('api/reference/<int:pk>/article/add', article.AddAPIView.as_view(), name='api_article_add'),
    path('api/reference/<int:pk>/article/list', article.ListAPIView.as_view(), name='api_article_list'),
    path('api/article/<int:pk>', article.RetrieveAPIView.as_view(), name='api_article_retrieve'),
    path('api/article/<int:pk>/update', article.UpdateAPIView.as_view(), name='api_article_update'),
    path('api/article/<int:pk>/delete', article.DeleteAPIView.as_view(), name='api_article_delete'),
    path('api/article/<int:pk>/file', article.FileAPIView.as_view(), name='api_article_file'),
]
