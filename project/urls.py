from django.urls import path
from .views import project, prefix

app_name = 'project'
urlpatterns = [
    path('new', project.NewView.as_view(), name='new'),
    path('list', project.ListView.as_view(), name='list'),
    path('list_all', project.ListAllView.as_view(), name='list_all'),
    path('project/<int:pk>', project.DetailView.as_view(), name='detail'),
    path('project/<int:pk>/update', project.UpdateView.as_view(), name='update'),
    path('project/<int:pk>/edit_note', project.EditNoteView.as_view(), name='edit_note'),
    path('search', project.SearchView.as_view(), name='search'),
    # API
    path('api/list', project.ListAPIView.as_view(), name='api_list'),
    path('api/project/<int:pk>', project.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/project/<int:pk>/member', project.MemberAPIView.as_view(), name='api_member'),
    # Prefix
    path('project/<int:pk>/prefix_add', prefix.AddView.as_view(), name='prefix_add'),
    path('project/<int:pk>/prefix_list', prefix.ListView.as_view(), name='prefix_list'),
    path('prefix/<int:pk>', prefix.DetailView.as_view(), name='prefix_detail'),
    path('prefix/<int:pk>/update', prefix.UpdateView.as_view(), name='prefix_update'),
    path('prefix/<int:pk>/edit_note', prefix.EditNoteView.as_view(), name='prefix_edit_note'),
    # Prefix API
    path('api/<int:pk>/prefix_add', prefix.AddAPIView.as_view(), name='api_prefix_add'),
    path('api/<int:pk>/prefix_list', prefix.ListAPIView.as_view(), name='api_prefix_list'),
    path('api/prefix/<int:pk>', prefix.RetrieveAPIView.as_view(), name='api_prefix_retrieve'),
    path('api/prefix/<int:pk>/update', prefix.UpdateAPIView.as_view(), name='api_prefix_update'),
]
