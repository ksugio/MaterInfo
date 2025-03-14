from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.module_loading import import_string
from django.utils.crypto import get_random_string
from django.forms import HiddenInput
from datetime import datetime
from config.settings import RANDOM_STRING_LENGTH
from . import base
from ..tasks import CloneTask, PullTask, PushTask
from .requests import GetSessionAccessToken, ParseURL
import os
import requests
import urllib
import json

class CloneView(base.FormView):
    model = None
    upper = None
    form_class = None
    remote_class = None
    remote_name = ''
    upper_name = ''
    template_name = "project/default_clone.html"
    title = ''
    success_name = ''
    view_name = ''
    view_args = 1
    scan_lower = True
    set_remote = True
    celery_task = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.remote_class:
            form.retrieve_name = self.remote_class.retrieve_name
        else:
            cls = import_string(self.remote_name)
            form.retrieve_name = cls.retrieve_name
        form.view_name = self.view_name
        form.view_args = self.view_args
        form.session = self.request.session
        form.host = self.request._current_scheme_host
        return form

    def form_valid(self, form):
        if form.auth:
            url = form.cleaned_data['url']
            rooturl, id, _ = ParseURL(url, self.view_name, self.view_args)
            if self.celery_task:
                if self.upper_name:
                    CloneTask.delay(self.remote_name, rooturl, id, form.access, form.auth, url, self.request.COOKIES,
                                    self.scan_lower, self.set_remote, self.upper_name, self.kwargs['pk'],
                                    request_user_id=self.request.user.id)
                else:
                    CloneTask.delay(self.remote_name, rooturl, id, form.access, form.auth, url, self.request.COOKIES,
                                    self.scan_lower, self.set_remote, '', 0, request_user_id=self.request.user.id)
            else:
                self.clone(rooturl, id, form.access, form.auth, url)
        return super().form_valid(form)

    def clone(self, rooturl, id, access, auth, url):
        remote = self.remote_class()
        option = {
            'rooturl': rooturl,
            'auth': auth,
            'cookies': self.request.COOKIES,
            'jwt_access': access,
            'scan_lower': self.scan_lower
        }
        clone_list = remote.clone_list(id, **option)
        if clone_list is not None:
            option = {
                'rooturl': rooturl,
                'auth': auth,
                'linkurl': url,
                'cookies': self.request.COOKIES,
                'jwt_access': access,
                'root_remoteid': id,
                'root_model': remote.model,
                'scan_lower': self.scan_lower,
                'set_remote': self.set_remote
            }
            if self.upper is not None:
                upper = self.upper.objects.get(pk=self.kwargs['pk'])
                kwargs, self.objects = remote.clone_exec(clone_list, upper, self.request.user, **option)
            else:
                kwargs, self.objects = remote.clone_exec(clone_list, None, self.request.user, **option)
            model = self.objects[0]
            if hasattr(model, 'remotelog'):
                remotelog = [{
                    'task': 'cloned',
                    'username': self.request.user.username,
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'lines': remote.get_pull_list_text(clone_list)
                }]
                model.remotelog = json.dumps(remotelog)
                model.save(localupd=False)

class ImportView(CloneView):
    scan_lower = False
    set_remote = False
    template_name = "project/default_import.html"
    hidden_lower = True
    default_lower = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.hidden_lower:
            form.fields['lower'].widget = HiddenInput()
        form.fields['lower'].initial = self.default_lower
        return form

    def form_valid(self, form):
        self.scan_lower = form.cleaned_data['lower']
        return super().form_valid(form)

class TokenView(base.View):
    model = None
    form_class = None
    template_name = "project/default_token.html"
    success_names = []

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        form = self.form_class()
        form.fields['url'].initial = model.remoteurl
        params = {
            'object': model,
            'form' : form,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = self.form_class(request.POST)
        form.session = request.session
        if form.is_valid():
            if form.access is not None:
                return redirect(reverse(self.success_names[kwargs['ind']], kwargs={'pk': model.id}))
        params = {
            'object': model,
            'form': form,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

class PullView(base.View):
    model = None
    remote_class = None
    remote_name = ''
    template_name = "project/default_pull.html"
    success_name = ''
    fail_name = ''
    celery_task = False

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        if model.remoteauth == 'JWT':
            access = GetSessionAccessToken(model.remoteurl, request.session)
            if access == 'NoToken' or access == 'InvalidToken':
                return redirect(reverse(self.fail_name, kwargs={'pk': model.id, 'ind': 0}))
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.remoteauth == 'JWT':
            access = GetSessionAccessToken(model.remoteurl, request.session)
            if access == 'NoToken' or access == 'InvalidToken':
                return redirect(reverse(self.fail_name, kwargs={'pk': model.id, 'ind': 0}))
        else:
            access = None
        if self.celery_task:
            model.task_id = ''
            model.remotelog = ''
            model.save(localupd=False)
            PullTask.delay(self.remote_name, self.kwargs['pk'], access, request.COOKIES,
                           request_user_id = request.user.id)
        else:
            self.pull(model, access, request)
        return redirect(self.get_success_url())

    def pull(self, model, access, request):
        option = {
            'rooturl': model.remoteurl,
            'auth': model.remoteauth,
            'cookies': request.COOKIES,
            'jwt_access': access,
            'scan_lower': True
        }
        remote = self.remote_class()
        pull_list = remote.pull_list(model, **option)
        option = {
            'rooturl': model.remoteurl,
            'auth': model.remoteauth,
            'linkurl': model.remotelink,
            'cookies': request.COOKIES,
            'jwt_access': access,
            'root_remoteid': model.remoteid,
            'root_model': remote.model,
            'scan_lower': True,
            'set_remote': True
        }
        remote.pull_exec(pull_list, model, request.user, **option)
        if hasattr(model, 'remotelog'):
            remotelog = json.loads(model.remotelog)
            remotelog.append({
                'task': 'pulled',
                'username': self.request.user.username,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'lines': remote.get_pull_list_text(pull_list)
            })
            model.remotelog = json.dumps(remotelog)
            model.save(localupd=False)

    def get_success_url(self):
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk']})

class PushView(base.View):
    model = None
    remote_class = None
    remote_name = ''
    template_name = "project/default_push.html"
    success_name = ''
    fail_name = ''
    celery_task = False

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        if model.remoteauth == 'JWT':
            access = GetSessionAccessToken(model.remoteurl, request.session)
            if access == 'NoToken' or access == 'InvalidToken':
                return redirect(reverse(self.fail_name, kwargs={'pk': model.id, 'ind': 1}))
        else:
            access = None
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.remoteauth == 'JWT':
            access = GetSessionAccessToken(model.remoteurl, request.session)
            if access == 'NoToken' or access == 'InvalidToken':
                return redirect(reverse(self.fail_name, kwargs={'pk': model.id, 'ind': 1}))
        else:
            access = None
        if self.celery_task:
            model.task_id = ''
            model.remotelog = ''
            model.save(localupd=False)
            PushTask.delay(self.remote_name, self.kwargs['pk'], access, request.COOKIES,
                           request_user_id=request.user.id)
        else:
            self.push(model, access, request)
        return redirect(self.get_success_url())

    def push(self, model, access, request):
        option = {
            'rooturl': model.remoteurl,
            'auth': model.remoteauth,
            'cookies': request.COOKIES,
            'jwt_access': access,
            'scan_lower': True
        }
        remote = self.remote_class()
        push_list = remote.push_list(model, **option)
        option = {
            'rooturl': model.remoteurl,
            'auth': model.remoteauth,
            'cookies': request.COOKIES,
            'jwt_access': access
        }
        remote.push_exec(push_list, **option)
        if hasattr(model, 'remotelog'):
            remotelog = json.loads(model.remotelog)
            remotelog.append({
                'task': 'pushed',
                'username': self.request.user.username,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'lines': remote.get_push_list_text(push_list)
            })
            model.remotelog = json.dumps(remotelog)
            model.save(localupd=False)

    def get_success_url(self):
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk']})

class LogView(base.View):
    model = None
    template_name = "project/default_log.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        if model.remotelog:
            params['remotelog'] = json.loads(model.remotelog)
        return render(request, self.template_name, params)

class SetRemoteView(base.FormView):
    model = None
    form_class = None
    remote_class = None
    template_name = "project/default_set_remote.html"
    title = ''
    success_name = ''
    view_name = ''
    view_args = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.retrieve_name = self.remote_class.retrieve_name
        form.view_name = self.view_name
        form.view_args = self.view_args
        form.session = self.request.session
        form.host = self.request._current_scheme_host
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['object'] = model
        return context

    def form_valid(self, form):
        if form.auth:
            url = form.cleaned_data['url']
            rooturl, id, _ = ParseURL(url, self.view_name, self.view_args)
            remote = self.remote_class()
            model = self.model.objects.get(pk=self.kwargs['pk'])
            option = {
                'rooturl': rooturl,
                'auth': form.auth,
                'linkurl': url,
                'cookies': self.request.COOKIES,
                'jwt_access': form.access,
                'root_model': remote.model,
                'id': id
            }
            remote.set_remote(model, self.request.user, **option)
            if hasattr(model, 'remotelog'):
                remotelog = [{
                    'task': 'set remote',
                    'username': self.request.user.username,
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'lines': []
                }]
                model.remotelog = json.dumps(remotelog)
                model.save(localupd=False)
        return super().form_valid(form)

class ClearRemoteView(base.View):
    model = None
    remote_class = None
    template_name = "project/default_clear_remote.html"
    success_name = ''

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        remote = self.remote_class()
        remote.clear_remote(model)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk']})

class Remote():
    model = None
    add_name = None
    list_name = None
    retrieve_name = None
    update_name = None
    delete_name = None
    serializer_class = None
    child_remote = []
    lower_remote = []
    synchronize = False
    ignore_push = False
    push_results = []
    UPDATE = 0
    ADD = 1
    DELETE = 2
    NOCHANGE = 3

    def __init__(self):
        if hasattr(self, 'lower_items'):
            self.lower_remote = []
            for item in self.lower_items:
                if 'Remote' in item:
                    cls = import_string(item['Remote'])
                    self.lower_remote.append(cls)

    def requests_get(self, url, **kwargs):
        if kwargs['auth'] == 'Cookie':
            headers = {'X-CSRFToken': kwargs['cookies']['csrftoken']}
            return requests.get(url, headers=headers, cookies=kwargs['cookies'])
        elif kwargs['auth'] == 'JWT':
            headers = {'Authorization': 'JWT %s' % (kwargs['jwt_access'])}
            return requests.get(url, headers=headers)

    # Clone functions
    def clone_list(self, rid, **kwargs):
        if self.retrieve_name is None:
            return None
        url = '%s%s' % (kwargs['rooturl'], reverse(self.retrieve_name, kwargs={'pk': rid}))
        response = self.requests_get(url, **kwargs)
        if response.status_code == 200:
            return self.pull_list_add(self.ADD, None, response.json(), **kwargs)
        else:
            return []

    def clone_exec(self, clone_list, upper, user, **kwargs):
        return self.pull_exec(clone_list, upper, user, **kwargs)

    # Pull functions
    def pull_list(self, model, **kwargs):
        if self.retrieve_name is None:
            return []
        url = '%s%s' % (kwargs['rooturl'], reverse(self.retrieve_name, kwargs={'pk': model.remoteid}))
        response = self.requests_get(url, **kwargs)
        if response.status_code == 200:
            return self.pull_list_add(self.UPDATE, model, response.json(), **kwargs)
        else:
            return []

    def pull_list_add(self, method, model, data, **kwargs):
        if method == self.UPDATE:
            if 'updated_at' in data:
                remoteat = datetime.fromisoformat(data['updated_at'])
            elif 'created_at' in data:
                remoteat = datetime.fromisoformat(data['created_at'])
            if remoteat > model.remoteat or model.localupd:
                objs = [(method, model, data, self.__class__)]
            else:
                objs = [(self.NOCHANGE, model, {}, self.__class__)]
        else:
            objs = [(method, model, data, self.__class__)]
        for child in self.child_remote:
            objs.append(child().pull_list_list(model, data, **kwargs))
        if kwargs['scan_lower']:
            for lower in self.lower_remote:
                objs.append(lower().pull_list_list(model, data, **kwargs))
        return objs

    def list(self, rid, **kwargs):
        if self.list_name is None:
            return None
        url = '%s%s' % (kwargs['rooturl'], reverse(self.list_name, kwargs={'pk': rid}))
        response = self.requests_get(url, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def pull_list_list(self, model, data, **kwargs):
        objs = []
        if model is None:
            rlist = self.list(data['id'], **kwargs)
            for remote in rlist:
                objs.extend(self.pull_list_add(self.ADD, None, remote, **kwargs))
        else:
            models = self.model.objects.filter(upper=model)
            rlist = self.list(model.remoteid, **kwargs)
            for remote in rlist:
                for local in models:
                    if hasattr(local, 'remoteurl') and local.remoteurl != '':
                        continue
                    elif remote['id'] == local.remoteid:
                        objs.extend(self.pull_list_add(self.UPDATE, local, remote, **kwargs))
                        break
                else:
                    objs.extend(self.pull_list_add(self.ADD, None, remote, **kwargs))
            if self.synchronize:
                for local in models:
                    for remote in rlist:
                        if local.remoteid == remote['id']:
                            break
                    else:
                        objs.extend(self.pull_list_add(self.DELETE, local, {}, **kwargs))
        return objs

    def pull_exec(self, pull_list, upper, user, **kwargs):
        objs = []
        object = None
        for item in pull_list:
            if isinstance(item, tuple):
                method, model, data, cls = item
                if method == self.UPDATE:
                    object, kwargs = cls().update(model, data, user, **kwargs)
                elif method == self.ADD:
                    object, kwargs = cls().create(data, upper, user, **kwargs)
                elif method == self.DELETE:
                    model.delete()
                elif method == self.NOCHANGE:
                    object = model
                objs.append(object)
            elif isinstance(item, list):
                kwargs, objsl = self.pull_exec(item, object, user, **kwargs)
                objs.append(objsl)
        return kwargs, objs

    def created_by(self, data, user, **kwargs):
        if 'created_by' in data and 'member' in kwargs:
            for usrl in kwargs['member']:
                if usrl[0]['id'] == data['created_by']:
                    return usrl[1]
        return user

    def updated_by(self, data, user, **kwargs):
        if 'updated_by' in data and 'member' in kwargs:
            for usrl in kwargs['member']:
                if usrl[0]['id'] == data['updated_by']:
                    return usrl[1]
        return user

    def create(self, data, upper, user, **kwargs):
        if hasattr(self.model, 'unique') and 'unique' in data:
            queryset = self.model.objects.filter(unique=data['unique'])
            if len(queryset) > 0:
                data['unique'] = get_random_string(length=RANDOM_STRING_LENGTH)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        option = { 'upper': upper }
        if kwargs['set_remote']:
            if hasattr(self.model, 'remoteurl') and self.model == kwargs['root_model']:
                option['remoteurl'] = kwargs['rooturl']
                option['remoteauth'] = kwargs['auth']
                option['remotelink'] = kwargs['linkurl']
            option['remoteid'] = data['id']
            if 'updated_at' in data:
                option['remoteat'] = data['updated_at']
            elif 'created_at' in data:
                option['remoteat'] = data['created_at']
        if hasattr(self.model, 'created_by'):
            option['created_by'] = self.created_by(data, user, **kwargs)
        if hasattr(self.model, 'updated_by'):
            option['updated_by'] = self.updated_by(data, user, **kwargs)
        object = serializer.save(**option)
        if kwargs['set_remote']:
            object.save(localupd=False)
        else:
            object.save()
        return object, kwargs

    def update(self, model, data, user, **kwargs):
        if hasattr(self.model, 'unique') and 'unique' in data:
            queryset = self.model.objects.filter(unique=data['unique'])
            if len(queryset) > 0:
                data['unique'] = get_random_string(length=RANDOM_STRING_LENGTH)
        serializer = self.serializer_class(model, data=data)
        serializer.is_valid(raise_exception=True)
        option = {}
        if 'rooturl' in kwargs:
            if hasattr(self.model, 'remoteurl') and self.model == kwargs['root_model']:
                option['remoteurl'] = kwargs['rooturl']
                option['remoteauth'] = kwargs['auth']
                option['remotelink'] = kwargs['linkurl']
                option['remoteid'] = data['id']
        if 'updated_at' in data:
            option['remoteat'] = data['updated_at']
        elif 'created_at' in data:
            option['remoteat'] = data['created_at']
        if hasattr(self.model, 'updated_by'):
            option['updated_by'] = self.updated_by(data, user, **kwargs)
        object = serializer.save(**option)
        object.save(localupd=False)
        return object, kwargs

    # Push functions
    def push_list(self, model, **kwargs):
        data = self.model_data(model)
        return self.push_list_add(self.UPDATE, model, data, **kwargs)

    def push_list_add(self, method, model, data, **kwargs):
        if self.ignore_push:
            objs = []
        else:
            if method == self.UPDATE or method == self.ADD:
                if model.localupd:
                    objs = [(method, model, data, self.__class__)]
                else:
                    objs = []
            else:
                objs = [(method, model, data, self.__class__)]
        for child in self.child_remote:
            objs.extend(child().push_list_list(model, **kwargs))
        if kwargs['scan_lower']:
            for lower in self.lower_remote:
                objs.extend(lower().push_list_list(model, **kwargs))
        return objs

    def push_list_list(self, model, **kwargs):
        models = self.model.objects.filter(upper=model)
        if model.remoteid:
            rlist = self.list(model.remoteid, **kwargs)
        else:
            rlist = []
        objs = []
        for local in models:
            if hasattr(local, 'remoteurl') and local.remoteurl != '':
                continue
            elif local.remoteid:
                for remote in rlist:
                    if local.remoteid == remote['id']:
                        data = self.model_data(local)
                        objs.extend(self.push_list_add(self.UPDATE, local, data, **kwargs))
                        break
            else:
                data = self.model_data(local)
                objs.extend(self.push_list_add(self.ADD, local, data, **kwargs))
        if self.synchronize:
            for remote in rlist:
                for local in models:
                    if remote['id'] == local.remoteid:
                        break
                else:
                    objs.extend(self.push_list_add(self.DELETE, None, remote, **kwargs))
        return objs

    def model_data(self, model):
        return self.serializer_class(model).data

    def push_exec(self, push_list, **kwargs):
        self.push_results = []
        for method, model, data, cls in push_list:
            remote_class = cls()
            if method == self.UPDATE:
                model, data, files, kwargs = remote_class.data_files(model, data, {}, **kwargs)
                result, kwargs = remote_class.put(model, data, files, **kwargs)
            elif method == self.ADD:
                model, data, files, kwargs = remote_class.data_files(model, data, {}, **kwargs)
                result, kwargs = remote_class.add(model, data, files, **kwargs)
            elif method == self.DELETE:
                result, kwargs = remote_class.delete(data, **kwargs)
            self.push_results.append(result)

    def data_files(self, model, data, files, **kwargs):
        del data['id']
        return model, data, files, kwargs

    def update_url(self, model, **kwargs):
        if self.update_name is not None:
            return '%s%s' % (kwargs['rooturl'], reverse(self.update_name, kwargs={'pk': model.remoteid}))
        else:
            return None

    def put(self, model, data, files, **kwargs):
        url = self.update_url(model, **kwargs)
        if url is None:
            return None, kwargs
        if kwargs['auth'] == 'Cookie':
            headers = {'X-CSRFToken': kwargs['cookies']['csrftoken']}
            response = requests.put(url, headers=headers, cookies=kwargs['cookies'], data=data, files=files)
        elif kwargs['auth'] == 'JWT':
            headers = {'Authorization': 'JWT %s' % (kwargs['jwt_access'])}
            response = requests.put(url, headers=headers, data=data, files=files)
        if response.status_code == 200:
            remote = response.json()
            if 'updated_at' in remote:
                model.remoteat = remote['updated_at']
            elif 'created_at' in remote:
                model.remoteat = remote['created_at']
            model.save(localupd=False)
            return remote, kwargs
        else:
            return None, kwargs

    def add_url(self, model, **kwargs):
        if self.add_name is not None:
            return '%s%s' % (kwargs['rooturl'], reverse(self.add_name, kwargs={'pk': model.upper.remoteid}))
        else:
            return None

    def add(self, model, data, files, **kwargs):
        url = self.add_url(model, **kwargs)
        if url is None:
            return None, kwargs
        if kwargs['auth'] == 'Cookie':
            headers = {'X-CSRFToken': kwargs['cookies']['csrftoken']}
            response = requests.post(url, headers=headers, cookies=kwargs['cookies'], data=data, files=files)
        elif kwargs['auth'] == 'JWT':
            headers = {'Authorization': 'JWT %s' % (kwargs['jwt_access'])}
            response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code == 201:
            remote = response.json()
            model.remoteid = remote['id']
            if 'updated_at' in remote:
                model.remoteat = remote['updated_at']
            elif 'created_at' in remote:
                model.remoteat = remote['created_at']
            model.save(localupd=False)
            return remote, kwargs
        else:
            return None, kwargs

    def delete_url(self, data, **kwargs):
        if self.delete_name is not None:
            return '%s%s' % (kwargs['rooturl'], reverse(self.delete_name, kwargs={'pk': data['id']}))
        else:
            return None

    def delete(self, data, **kwargs):
        url = self.delete_url(data, **kwargs)
        if url is None:
            return None
        if kwargs['auth'] == 'Cookie':
            headers = {'X-CSRFToken': kwargs['cookies']['csrftoken']}
            response = requests.delete(url, headers=headers, cookies=kwargs['cookies'])
        elif kwargs['auth'] == 'JWT':
            headers = {'Authorization': 'JWT %s' % (kwargs['jwt_access'])}
            response = requests.delete(url, headers=headers)
        return response, kwargs

    # Set Remote functions
    def set_remote(self, model, user, **kwargs):
        if self.retrieve_name is None:
            return None
        url = '%s%s' % (kwargs['rooturl'], reverse(self.retrieve_name, kwargs={'pk': kwargs['id']}))
        response = self.requests_get(url, **kwargs)
        if response.status_code == 200:
            object, kwargs = self.update(model, response.json(), user, **kwargs)
            self.clear_child_lower(object)
        else:
            return None

    def clear_remote(self, model, **kwargs):
        model.remoteurl = ''
        model.remoteauth = ''
        model.remotelink = ''
        model.remotelog = ''
        model.remoteid = None
        model.remoteat = None
        if hasattr(model, 'remotelog'):
            model.remotelog = ''
        model.save()
        self.clear_child_lower(model, **kwargs)

    def clear_child_lower(self, model, **kwargs):
        for child in self.child_remote:
            child().clear_child_lower_clear(model)
        for lower in self.lower_remote:
            lower().clear_child_lower_clear(model)

    def clear_child_lower_clear(self, model, **kwargs):
        models = self.model.objects.filter(upper=model)
        for local in models:
            if hasattr(local, 'remoteurl') and local.remoteurl != '':
                continue
            else:
                local.remoteurl = ''
                local.remoteauth = ''
                local.remotelink = ''
                local.remoteid = None
                local.remoteat = None
                local.save()
                self.clear_child_lower(local, **kwargs)

    def get_pull_list_text(self, pull_list, line_max=256):
        lines = []
        for item in pull_list:
            if isinstance(item, tuple):
                method, model, data, cls = item
                if 'created_by' in data:
                    data.pop('created_by')
                if 'created_at' in data:
                    data.pop('created_at')
                if 'updated_by' in data:
                    data.pop('updated_by')
                if 'updated_at' in data:
                    data.pop('updated_at')
                if method == self.UPDATE and model:
                    line = 'Update: %s(local %d) < %s' % (model.__class__.__name__, model.id, data)
                    lines.append(line[:line_max])
                elif method == self.ADD:
                    line = 'Add: %s %s' % (cls.model.__name__, data)
                    lines.append(line[:line_max])
                elif method == self.DELETE and model:
                    line = 'Delete: %s(local %d)' % (model.__class__.__name__, model.id)
                    lines.append(line[:line_max])
            elif isinstance(item, list):
                lines.extend(self.get_pull_list_text(item))
        return lines

    def get_push_list_text(self, push_list, line_max=256):
        lines = []
        for method, model, data, cls in push_list:
            if 'created_by' in data:
                data.pop('created_by')
            if 'created_at' in data:
                data.pop('created_at')
            if 'updated_by' in data:
                data.pop('updated_by')
            if 'updated_at' in data:
                data.pop('updated_at')
            if method == self.UPDATE:
                line = 'Update: %s(remote %d) < %s' % (model.__class__.__name__, model.remoteid, data)
                lines.append(line[:line_max])
            elif method == self.ADD:
                line = 'Add: %s %s' % (model.__class__.__name__, data)
                lines.append(line[:line_max])
            elif method == self.DELETE:
                line = 'Delete: %s(remote %d)' % (cls.model.__name__, data['id'])
                lines.append(line[:line_max])
        return lines

class FileRemote(Remote):
    file_fields_names = []

    def download(self, name, id, **kwargs):
        url = '%s%s' % (kwargs['rooturl'], reverse(name, kwargs={'pk': id}))
        file = self.requests_get(url, **kwargs)
        if file.status_code == 200 and 'Content-Disposition' in file.headers:
            dispo = file.headers['Content-Disposition']
            fname = dispo[dispo.find('filename=')+9:].strip('"')
            return InMemoryUploadedFile(ContentFile(file.content), None, fname, None, len(file.content), None)
        else:
            return None

    def create(self, data, upper, user, **kwargs):
        for field, name in self.file_fields_names:
            if field in data:
                if data[field] is not None:
                    prev = data[field]
                    data[field] = self.download(name, data['id'], **kwargs)
                else:
                    del data[field]
        object, kwargs = super().create(data, upper, user, **kwargs)
        for field, name in self.file_fields_names:
            if field in data:
                file = getattr(object, field)
                if file:
                    path = urllib.parse.urlparse(prev).path
                    field_local = field + '_local'
                    if field_local not in kwargs:
                        kwargs[field_local] = { path: file.url }
                    else:
                        kwargs[field_local][path] = file.url
        return object, kwargs

    def update(self, model, data, user, **kwargs):
        for field, name in self.file_fields_names:
            if field in data:
                if data[field] is not None:
                    prev = data[field]
                    data[field] = self.download(name, data['id'], **kwargs)
                else:
                    del data[field]
        object, kwargs = super().update(model, data, user, **kwargs)
        for field, name in self.file_fields_names:
            if field in data:
                file = getattr(object, field)
                if file:
                    path = urllib.parse.urlparse(prev).path
                    field_local = field + '_local'
                    if field_local not in kwargs:
                        kwargs[field_local] = { path: file.url }
                    else:
                        kwargs[field_local][path] = file.url
        return object, kwargs

    def fileopen(self, file):
        split = os.path.splitext(os.path.basename(file.name))
        tail = split[0].rfind('_')
        fname = '%s%s' % (split[0][:tail], split[1])
        return (fname, file.open(mode='rb'))

    def data_files(self, model, data, files, **kwargs):
        model, data, files, kwargs = super().data_files(model, data, files, **kwargs)
        for field, name in self.file_fields_names:
            if field in data:
                if data[field] is not None:
                    files[field] = self.fileopen(model.file)
                del data[field]
        return model, data, files, kwargs

    def put(self, model, data, files, **kwargs):
        remote, kwargs = super().put(model, data, files, **kwargs)
        for field, name in self.file_fields_names:
            if hasattr(model, field):
                file = getattr(model, field)
                if file:
                    path = urllib.parse.urlparse(remote[field]).path
                    field_remote = field + '_remote'
                    if field_remote not in kwargs:
                        kwargs[field_remote] = { file.url : path }
                    else:
                        kwargs[field_remote][file.url] = path
        return remote, kwargs

    def add(self, model, data, files, **kwargs):
        remote, kwargs = super().add(model, data, files, **kwargs)
        for field, name in self.file_fields_names:
            if hasattr(model, field):
                file = getattr(model, field)
                if file:
                    path = urllib.parse.urlparse(remote[field]).path
                    field_remote = field + '_remote'
                    if field_remote not in kwargs:
                        kwargs[field_remote] = { file.url : path }
                    else:
                        kwargs[field_remote][file.url] = path
        return remote, kwargs

class SwitchRemote(Remote):
    upper_save = False

    def data_switcher(self, data):
        pass

    def list(self, rid, **kwargs):
        org_list = super().list(rid, **kwargs)
        new_list = []
        for data in org_list:
            remote_class = self.data_switcher(data)
            if remote_class is not None and remote_class.retrieve_name is not None:
                url = '%s%s' % (kwargs['rooturl'], reverse(remote_class.retrieve_name, kwargs={'pk': data['id']}))
                response = self.requests_get(url, **kwargs)
                if response.status_code == 200:
                    new_list.append(response.json())
        return new_list

    def create(self, data, upper, user, **kwargs):
        remote_class = self.data_switcher(data)
        if hasattr(remote_class, 'modify_pull'):
            project = base.ProjectModel(upper)
            data = remote_class.modify_pull(data, project)
        serializer = remote_class.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        option = {
            'upper': upper,
            'updated_by': self.updated_by(data, user, **kwargs)
        }
        if kwargs['set_remote']:
            option['remoteid'] = data['id']
            option['remoteat'] = data['updated_at']
        object = serializer.save(**option)
        if kwargs['set_remote']:
            object.save(localupd=False)
            if self.upper_save:
                object.upper.save(localupd=False)
        else:
            object.save()
            if self.upper_save:
                object.upper.save()
        return object, kwargs

    def model_switcher(self, model):
        pass

    def update(self, model, data, user, **kwargs):
        remote_class = self.model_switcher(model)
        entity = remote_class.model.objects.get(id=model.id)
        if hasattr(remote_class, 'modify_pull'):
            project = base.ProjectModel(model)
            data = remote_class.modify_pull(data, project)
        serializer = remote_class.serializer_class(entity, data=data)
        serializer.is_valid(raise_exception=True)
        option = {
            'updated_by': self.updated_by(data, user, **kwargs),
            'remoteat': data['updated_at']
        }
        object = serializer.save(**option)
        object.save(localupd=False)
        if self.upper_save:
            object.upper.save(localupd=False)
        return object, kwargs

    def model_data(self, model):
        remote_class = self.model_switcher(model)
        if remote_class is not None:
            entity = remote_class.model.objects.get(id=model.id)
            return remote_class.serializer_class(entity).data
        else:
            return super().model_data(model)

    def data_files(self, model, data, files, **kwargs):
        remote_class = self.model_switcher(model)
        if hasattr(remote_class, 'modify_push'):
            entity = remote_class.model.objects.get(id=model.id)
            data = remote_class.modify_push(entity, data)
        return super().data_files(model, data, files, **kwargs)

    def update_url(self, model, **kwargs):
        remote_class = self.model_switcher(model)
        if remote_class is not None and remote_class.update_name is not None:
            return '%s%s' % (kwargs['rooturl'], reverse(remote_class.update_name, kwargs={'pk': model.remoteid}))
        else:
            return None

    def add_url(self, model, **kwargs):
        remote_class = self.model_switcher(model)
        if remote_class is not None and remote_class.add_name is not None:
            return '%s%s' % (kwargs['rooturl'], reverse(remote_class.add_name, kwargs={'pk': model.upper.remoteid}))
        else:
            return None
