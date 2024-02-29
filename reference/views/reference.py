#from django.shortcuts import render, redirect
from project.views import base, base_api, remote
from project.models import Project
from project.forms import EditNoteForm, ImportForm, CloneForm, TokenForm, SetRemoteForm, SearchForm
from ..models import Reference
from ..serializer import ReferenceSerializer
from .article import ArticleRemote

class AddView(base.AddView):
    model = Reference
    upper = Project
    fields = ('title', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Reference
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'reference:add'],
                  ['Import', 'reference:import'],
                  ['Clone', 'reference:clone'],
                  ['Search', 'reference:search']]

class DetailView(base.DetailView):
    model = Reference
    template_name = "reference/reference_detail.html"
    navigation = [['Article', 'reference:article_list'], ]

class UpdateView(base.UpdateView):
    model = Reference
    fields = ('title', 'status', 'note')
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Reference
    template_name = "project/default_delete.html"

class EditNoteView(base.EditNoteView):
    model = Reference
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class SearchView(base.SearchView):
    model = Reference
    upper = Project
    form_class = SearchForm
    template_name = "reference/reference_search.html"
    title = 'Reference Search'
    session_name = 'reference_search'
    back_name = 'reference:list'
    lower_items = [{'Search': 'reference.views.article.ArticleSearch'}]

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = ReferenceSerializer

class ListAPIView(base_api.ListAPIView):
    model = Reference
    upper = Project
    serializer_class = ReferenceSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Reference
    serializer_class = ReferenceSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Reference
    serializer_class = ReferenceSerializer

class ReferenceRemote(remote.Remote):
    model = Reference
    add_name = 'reference:api_add'
    list_name = 'reference:api_list'
    retrieve_name = 'reference:api_retrieve'
    update_name = 'reference:api_update'
    serializer_class = ReferenceSerializer
    lower_remote = [ArticleRemote]

class ImportView(remote.ImportView):
    model = Reference
    upper = Project
    form_class = ImportForm
    remote_class = ReferenceRemote
    template_name = "project/default_import.html"
    title = 'Reference Import'
    success_name = 'reference:list'
    view_name = 'reference:detail'
    hidden_lower = False
    default_lower = True

class CloneView(remote.CloneView):
    model = Reference
    form_class = CloneForm
    upper = Project
    remote_class = ReferenceRemote
    template_name = "project/default_clone.html"
    title = 'Reference Clone'
    success_name = 'reference:list'
    view_name = 'reference:detail'

class TokenView(remote.TokenView):
    model = Reference
    form_class = TokenForm
    success_names = ['reference:pull', 'reference:push']

class PullView(remote.PullView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
    fail_name = 'reference:token'

class PushView(remote.PushView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
    fail_name = 'reference:token'

class SetRemoteView(remote.SetRemoteView):
    model = Reference
    form_class = SetRemoteForm
    remote_class = ReferenceRemote
    title = 'Reference Set Remote'
    success_name = 'reference:detail'
    view_name = 'reference:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Reference
    remote_class = ReferenceRemote
    success_name = 'reference:detail'
