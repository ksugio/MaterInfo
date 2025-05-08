from django.urls import path
from .views import project, prefix, task

def UrlPatterns(views, name):
    urlpatterns = []
    if hasattr(views, 'AddView'):
        urlpatterns.append(path('<int:pk>/%s/add' % name, views.AddView.as_view(), name='%s_add' % name)),
    if hasattr(views, 'ImportView'):
        urlpatterns.append(path('<int:pk>/%s/import' % name, views.ImportView.as_view(), name='%s_import' % name))
    if hasattr(views, 'ListView'):
        urlpatterns.append(path('<int:pk>/%s/list' % name, views.ListView.as_view(), name='%s_list' % name))
    if hasattr(views, 'DetailView'):
        urlpatterns.append(path('%s/<int:pk>' % name, views.DetailView.as_view(), name='%s_detail' % name))
    if hasattr(views, 'UpdateView'):
        urlpatterns.append(path('%s/<int:pk>/update' % name, views.UpdateView.as_view(), name='%s_update' % name))
    if hasattr(views, 'EditNoteView'):
        urlpatterns.append(path('%s/<int:pk>/edit_note' % name, views.EditNoteView.as_view(), name='%s_edit_note' % name))
    if hasattr(views, 'DeleteView'):
        urlpatterns.append(path('%s/<int:pk>/delete' % name, views.DeleteView.as_view(), name='%s_delete' % name))
    if hasattr(views, 'MoveView'):
        urlpatterns.append(path('%s/<int:pk>/move' % name, views.MoveView.as_view(), name='%s_move' % name))
    if hasattr(views, 'ImageView'):
        urlpatterns.append(path('%s/<int:pk>/image' % name, views.ImageView.as_view(), name='%s_image' % name))
    if hasattr(views, 'PlotView'):
        urlpatterns.append(path('%s/<int:pk>/plot' % name, views.PlotView.as_view(), name='%s_plot' % name))
    if hasattr(views, 'TableView'):
        urlpatterns.append(path('%s/<int:pk>/table' % name, views.TableView.as_view(), name='%s_table' % name))
    if hasattr(views, 'DownloadView'):
        urlpatterns.append(path('%s/<int:pk>/download' % name, views.DownloadView.as_view(), name='%s_download' % name))
    if hasattr(views, 'RevokeView'):
        urlpatterns.append(path('%s/<int:pk>/revoke' % name, views.RevokeView.as_view(), name='%s_revoke' % name))
    if hasattr(views, 'FileView'):
        urlpatterns.append(path('%s/<int:pk>/file' % name, views.FileView.as_view(), name='%s_file' % name))
    if hasattr(views, 'File2View'):
        urlpatterns.append(path('%s/<int:pk>/file2' % name, views.File2View.as_view(), name='%s_file2' % name))
    if hasattr(views, 'File3View'):
        urlpatterns.append(path('%s/<int:pk>/file3' % name, views.File3View.as_view(), name='%s_file3' % name))
    return urlpatterns

def UrlPatternsAPI(views, name):
    urlpatterns = []
    if hasattr(views, 'AddAPIView'):
        urlpatterns.append(path('api/<int:pk>/%s/add' % name, views.AddAPIView.as_view(), name='api_%s_add' % name))
    if hasattr(views, 'ListAPIView'):
        urlpatterns.append(path('api/<int:pk>/%s/list' % name, views.ListAPIView.as_view(), name='api_%s_list' % name))
    if hasattr(views, 'RetrieveAPIView'):
        urlpatterns.append(path('api/%s/<int:pk>' % name, views.RetrieveAPIView.as_view(), name='api_%s_retrieve' % name))
    if hasattr(views, 'UpdateAPIView'):
        urlpatterns.append(path('api/%s/<int:pk>/update' % name, views.UpdateAPIView.as_view(), name='api_%s_update' % name))
    if hasattr(views, 'DeleteAPIView'):
        urlpatterns.append(path('api/%s/<int:pk>/delete' % name, views.DeleteAPIView.as_view(), name='api_%s_delete' % name))
    if hasattr(views, 'FileAPIView'):
        urlpatterns.append(path('api/%s/<int:pk>/file' % name, views.FileAPIView.as_view(), name='api_%s_file' % name))
    if hasattr(views, 'File2APIView'):
        urlpatterns.append(path('api/%s/<int:pk>/file2' % name, views.File2APIView.as_view(), name='api_%s_file2' % name))
    if hasattr(views, 'File3APIView'):
        urlpatterns.append(path('api/%s/<int:pk>/file3' % name, views.File3APIView.as_view(), name='api_%s_file3' % name))
    return urlpatterns

app_name = 'project'
urlpatterns = [
    path('new', project.NewView.as_view(), name='new'),
    # path('clone', project.CloneView.as_view(), name='clone'),
    path('list/<int:order>/<int:size>', project.ListView.as_view(), name='list'),
    path('list_all/<int:order>/<int:size>', project.ListAllView.as_view(), name='list_all'),
    path('project/<int:pk>', project.DetailView.as_view(), name='detail'),
    path('project/<int:pk>/update', project.UpdateView.as_view(), name='update'),
    path('project/<int:pk>/edit_note', project.EditNoteView.as_view(), name='edit_note'),
    path('project/<int:pk>/token/<int:ind>', project.TokenView.as_view(), name='token'),
    # path('project/<int:pk>/pull', project.PullView.as_view(), name='pull'),
    # path('project/<int:pk>/push', project.PushView.as_view(), name='push'),
    path('project/<int:pk>/log', project.LogView.as_view(), name='log'),
    # path('project/<int:pk>/set_remote', project.SetRemoteView.as_view(), name='set_remote'),
    path('project/<int:pk>/clear_remote', project.ClearRemoteView.as_view(), name='clear_remote'),
    path('search', project.SearchView.as_view(), name='search'),
    # API
    path('api/list', project.ListAPIView.as_view(), name='api_list'),
    path('api/project/<int:pk>', project.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/project/<int:pk>/update', project.UpdateAPIView.as_view(), name='api_update'),
    path('api/project/<int:pk>/member', project.MemberAPIView.as_view(), name='api_member'),
    # Task
    path('task_user', task.TaskUserView.as_view(), name='task_user'),
    path('task_all', task.TaskAllView.as_view(), name='task_all'),
    path('task_delete/<str:task_id>/<int:ind>', task.TaskDeleteView.as_view(), name='task_delete'),
    path('task_revoke/<str:task_id>/<int:ind>', task.TaskRevokeView.as_view(), name='task_revoke'),
    path('restart_daemon', task.RestartDaemonView.as_view(), name='restart_daemon')
]
urlpatterns += UrlPatterns(prefix, 'prefix')
urlpatterns += UrlPatternsAPI(prefix, 'prefix')



