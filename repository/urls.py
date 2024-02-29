from django.urls import path
from .views import repository, git

app_name = 'repository'
urlpatterns = [
    path('<int:pk>/add', repository.AddView.as_view(), name='add'),
    path('<int:pk>/clone', repository.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', repository.ListView.as_view(), name='list'),
    path('repository/<int:pk>/detail/<str:branch>/<str:hexsha>', repository.DetailView.as_view(), name='detail'),
    path('repository/<int:pk>/update', repository.UpdateView.as_view(), name='update'),
    path('repository/<int:pk>/download', repository.DownloadView.as_view(), name='download'),
    path('repository/<int:pk>/branches', repository.BranchesView.as_view(), name='branches'),
    path('repository/<int:pk>/new_branch', repository.NewBranchView.as_view(), name='new_branch'),
    path('repository/<int:pk>/delete_branch/<str:branch>', repository.DeleteBranchView.as_view(), name='delete_branch'),
    # git server
    path('git/<int:pid>/<str:name>/info/refs', git.info_refs, name='info_refs'),
    path('git/<int:pid>/<str:name>/git-upload-pack', git.git_upload_pack, name='git_upload_pack'),
    path('git/<int:pid>/<str:name>/git-receive-pack', git.git_receive_pack, name='git_receive_pack'),
]
