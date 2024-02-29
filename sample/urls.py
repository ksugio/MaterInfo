from django.urls import path
from . import views

app_name = 'sample'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/import', views.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', views.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('<int:pk>/search', views.SearchView.as_view(), name='search'),
    path('sample/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('sample/<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('sample/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('sample/<int:pk>/edit_note', views.EditNoteView.as_view(), name='edit_note'),
    path('sample/<int:pk>/token/<int:ind>', views.TokenView.as_view(), name='token'),
    path('sample/<int:pk>/pull', views.PullView.as_view(), name='pull'),
    path('sample/<int:pk>/push', views.PushView.as_view(), name='push'),
    path('sample/<int:pk>/set_remote', views.SetRemoteView.as_view(), name='set_remote'),
    path('sample/<int:pk>/clear_remote', views.ClearRemoteView.as_view(), name='clear_remote'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/sample/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/sample/<int:pk>/update', views.UpdateAPIView.as_view(), name='api_update'),
]
