from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.module_loading import import_string
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from config.settings import PROJECT_LOWER
from accounts.models import CustomUser
from . import base, base_api, remote, task
from ..models import Project
from ..forms import CloneForm, TokenForm, SetRemoteForm, SearchForm, ProjectAddForm, ProjectUpdateForm
from ..serializer import ProjectSerializer, MemberSerializer

class NewView(base.AddView):
    model = Project
    form_class = ProjectAddForm
    template_name ="project/default_add.html"
    title = 'Project New'

    def test_func(self):
        return self.request.user.is_manager

class ListView(base.ListView):
    model = Project
    template_name = "project/default_list.html"
    change_order = True
    change_paginate = True
    title = 'Project'

    def test_func(self):
        return True

    def get_queryset(self):
        if self.kwargs['size'] == 0:
            self.paginate_by = 10
        elif self.kwargs['size'] == 1:
            self.paginate_by = 20
        elif self.kwargs['size'] == 2:
            self.paginate_by = 50
        elif self.kwargs['size'] == 3:
            self.paginate_by = 100
        elif self.kwargs['size'] == 4:
            self.paginate_by = 200
        elif self.kwargs['size'] == 5:
            self.paginate_by = 500
        order = self.kwargs['order']
        if order == 0 and hasattr(self.model, 'created_by'):
            return self.model.objects.filter(member=self.request.user).order_by('-created_at')
        elif order == 1 and hasattr(self.model, 'created_by'):
            return self.model.objects.filter(member=self.request.user).order_by('created_at')
        elif order == 2 and hasattr(self.model, 'updated_by'):
            return self.model.objects.filter(member=self.request.user).order_by('-updated_at')
        elif order == 3 and hasattr(self.model, 'updated_by'):
            return self.model.objects.filter(member=self.request.user).order_by('updated_at')
        elif order == 4 and hasattr(self.model, 'title'):
            return self.model.objects.filter(member=self.request.user).order_by('title')
        elif order == 5 and hasattr(self.model, 'title'):
            return self.model.objects.filter(member=self.request.user).order_by('-title')
        else:
            return self.model.objects.filter(member=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_manager:
            context['navigation_list'] = [
                base.Link('New', reverse('project:new')),
                # base.Link('Clone', reverse('project:clone')),
                base.Link('All', reverse('project:list_all', kwargs={'order': 0, 'size': 0})),
                base.Link('Search', reverse('project:search'))
            ]
        return context

class ListAllView(base.ListView):
    model = Project
    template_name = "project/default_list.html"
    change_order = True
    change_paginate = True
    title = 'Project All'

    def test_func(self):
        return self.request.user.is_manager

    def get_queryset(self):
        if self.kwargs['size'] == 0:
            self.paginate_by = 10
        elif self.kwargs['size'] == 1:
            self.paginate_by = 20
        elif self.kwargs['size'] == 2:
            self.paginate_by = 50
        elif self.kwargs['size'] == 3:
            self.paginate_by = 100
        elif self.kwargs['size'] == 4:
            self.paginate_by = 200
        elif self.kwargs['size'] == 5:
            self.paginate_by = 500
        order = self.kwargs['order']
        if order == 0 and hasattr(self.model, 'created_by'):
            return self.model.objects.all().order_by('-created_at')
        elif order == 1 and hasattr(self.model, 'created_by'):
            return self.model.objects.all().order_by('created_at')
        elif order == 2 and hasattr(self.model, 'updated_by'):
            return self.model.objects.all().order_by('-updated_at')
        elif order == 3 and hasattr(self.model, 'updated_by'):
            return self.model.objects.all().order_by('updated_at')
        elif order == 4 and hasattr(self.model, 'title'):
            return self.model.objects.all().order_by('title')
        elif order == 5 and hasattr(self.model, 'title'):
            return self.model.objects.all().order_by('-title')
        else:
            return self.model.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_manager:
            context['navigation_list'] = [
                base.Link('New', reverse('project:new')),
                base.Link('Member', reverse('project:list', kwargs={'order': 0, 'size': 0})),
            ]
        return context

class DetailView(task.DetailView):
    model = Project
    template_name = "project/project_detail.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(model) or self.request.user.is_manager

    def get_context_data(self, **kwargs):
        self.navigation = []
        for item in PROJECT_LOWER:
            if 'ListName' in item:
                self.navigation.append(item['ListName'])
        return super().get_context_data(**kwargs)

class UpdateView(base.UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = "project/default_update.html"

    def test_func(self):
         model = get_object_or_404(self.model, id=self.kwargs['pk'])
         return self.request.user == model.created_by or self.request.user.is_manager

class EditNoteView(base.MDEditView):
    model = Project
    text_field = 'note'
    template_name = "project/default_mdedit.html"

    def test_func(self):
         model = get_object_or_404(self.model, id=self.kwargs['pk'])
         return self.request.user == model.created_by or self.request.user.is_manager

class SearchView(base.SearchView):
    model = Project
    form_class = SearchForm
    template_name = "project/default_search.html"
    title = 'Project Search'
    session_name = 'project_search'
    back_name = "project:list"
    back_kwargs = {'order': 0, 'size': 0}
    lower_items = PROJECT_LOWER

    def test_func(self):
        return True

    def get_models(self, upper):
        return self.model.objects.filter(member=self.request.user)

class ProjectRemote(remote.Remote):
    model = Project
    list_name = 'project:api_list'
    retrieve_name = 'project:api_retrieve'
    serializer_class = ProjectSerializer
    member_name = 'project:api_member'
    ignore_push = True

    def __init__(self):
        super().__init__()
        remotes = []
        for item in PROJECT_LOWER:
            if 'Remote' in item:
                remotes.append([item['RemoteOrder'], item['Remote']])
        remotes.sort()
        self.lower_remote = []
        for item in remotes:
            cls = import_string(item[1])
            self.lower_remote.append(cls)

    def member_list(self, rid, **kwargs):
        url = '%s%s' % (kwargs['rooturl'], reverse(self.member_name, kwargs={'pk': rid}))
        response = self.requests_get(url, **kwargs)
        if response.status_code != 200:
            return []
        member = []
        for ruser in response.json():
            local = CustomUser.objects.filter(username=ruser['username'])
            if len(local) == 1:
                member.append([ruser, local[0]])
        return member

    def pull_exec(self, pull_list, upper, user, **kwargs):
        if not 'member' in kwargs:
            rrid = kwargs.pop('root_remoteid')
            kwargs['member'] = self.member_list(rrid, **kwargs)
        return super().pull_exec(pull_list, upper, user, **kwargs)

    def create(self, data, upper, user, **kwargs):
        if 'member' in kwargs and len(kwargs['member']) > 0:
            data['member'] = [member[1].id for member in kwargs['member']]
        else:
            data['member'] = [user.id]
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        option = {
            'created_by': self.created_by(data, user, **kwargs),
            'updated_by': self.updated_by(data, user, **kwargs),
            'remoteurl': kwargs['rooturl'],
            'remoteauth': kwargs['auth'],
            'remotelink': kwargs['linkurl'],
            'remoteid': data['id'],
            'remoteat': data['updated_at']
        }
        object = serializer.save(**option)
        object.save(localupd=False)
        return object, kwargs

    def update(self, model, data, user, **kwargs):
        if 'member' in kwargs and len(kwargs['member']) > 0:
            data['member'] = [member[1].id for member in kwargs['member']]
        else:
            data['member'] = [member.id for member in model.member.all()]
        serializer = self.serializer_class(model, data=data)
        serializer.is_valid(raise_exception=True)
        if 'rooturl' in kwargs:
            option = {
                'updated_by': self.updated_by(data, user, **kwargs),
                'remoteurl': kwargs['rooturl'],
                'remoteauth': kwargs['auth'],
                'remotelink': kwargs['linkurl'],
                'remoteid': data['id'],
                'remoteat': data['updated_at']
            }
        else:
            option = {
                'updated_by': self.updated_by(data, user, **kwargs),
                'remoteat': data['updated_at']
            }
        object = serializer.save(**option)
        object.save(localupd=False)
        return object, kwargs

class CloneView(remote.CloneView):
    model = Project
    form_class = CloneForm
    remote_class = ProjectRemote
    remote_name = 'project.views.project.ProjectRemote'
    title = 'Project Clone'
    template_name = "project/default_clone.html"
    success_name = 'project:list'
    success_kwargs = {'order': 0, 'size': 0}
    view_name = 'project:detail'
    celery_task = True

    def test_func(self):
        return self.request.user.is_manager

    def get_success_url(self):
        return reverse(self.success_name, kwargs=self.success_kwargs)

class TokenView(remote.TokenView):
    model = Project
    form_class = TokenForm
    success_names = ['project:pull', 'project:push']
    view_name = 'project:detail'

    def test_func(self):
        return self.request.user.is_manager

class PullView(remote.PullView):
    model = Project
    remote_class = ProjectRemote
    remote_name = 'project.views.project.ProjectRemote'
    success_name = 'project:detail'
    fail_name = 'project:token'
    celery_task = True

    def test_func(self):
        return self.request.user.is_manager

class PushView(remote.PushView):
    model = Project
    remote_class = ProjectRemote
    remote_name = 'project.views.project.ProjectRemote'
    success_name = 'project:detail'
    fail_name = 'project:token'
    celery_task = True

    def test_func(self):
        return self.request.user.is_manager

class LogView(remote.LogView):
    model = Project

class SetRemoteView(remote.SetRemoteView):
    model = Project
    form_class = SetRemoteForm
    remote_class = ProjectRemote
    title = 'Project Set Remote'
    success_name = 'project:detail'
    view_name = 'project:detail'

    def test_func(self):
        return self.request.user.is_manager

class ClearRemoteView(remote.ClearRemoteView):
    model = Project
    remote_class = ProjectRemote
    success_name = 'project:detail'

    def test_func(self):
        return self.request.user.is_manager

# API
class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.model.objects.filter(member=self.request.user).order_by('-created_at')

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    permission_classes = (IsAuthenticated, base_api.IsManagerOrCreateUser)
    model = Project
    serializer_class = ProjectSerializer

class MemberAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, base_api.IsMember)
    model = Project
    serializer_class = MemberSerializer

    def get_queryset(self):
        project = self.model.objects.get(pk=self.kwargs['pk'])
        return project.member.all()
