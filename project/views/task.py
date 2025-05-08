from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.module_loading import import_string
from config.settings import TASK_MODELS, RESTART_DAEMON
from config.celery import app
from accounts.models import CustomUser
from . import base
from ..forms import RestartDaemonForm
from django_celery_results.models import TaskResult
from celery.result import AsyncResult
import time
import json
import subprocess
import os

def ReadDeleteFile(path, name):
    fullpath = os.path.join(path, name)
    if os.path.exists(fullpath):
        with open(fullpath, 'r') as f:
            data = f.read()
        os.remove(fullpath)
        return data
    else:
        return None

class AddView(base.AddView):
    model = None
    upper = None
    template_name = "project/default_add.html"

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        if hasattr(self, 'start_task'):
            self.start_task(form, model)
        return super().form_valid(form)

class DetailView(base.DetailView):
    model = None
    template_name = "collect/regreshap_detail.html"
    result_fields = ()

    def result_saved(self, model):
        for field in self.result_fields:
            if hasattr(model, field) and not getattr(model, field):
                return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        result = TaskResult.objects.filter(task_id=model.task_id)
        if result:
            status = result[0].status
            dsec = (result[0].date_done - result[0].date_created).total_seconds()
            if hasattr(self, 'set_model'):
                if status == 'SUCCESS' and not self.result_saved(model):
                    self.set_model(model, json.loads(result[0].result))
                    model.save()
                    context['object'] = model
        elif self.result_saved(model):
            status = 'SAVED'
            dsec = 0.0
        elif not model.task_id:
            status = 'UNKNOWN'
            dsec = 0.0
        else:
            task = AsyncResult(model.task_id)
            status = task.status
            dsec = 0.0
        context['task_status'] = status
        context['task_time'] = dsec
        return context

class UpdateView(base.UpdateView):
    model = None
    template_name = "project/default_update.html"

    def task_started(self, model):
        result = TaskResult.objects.filter(task_id=model.task_id)
        if result:
            if result[0].status == 'STARTED':
                return True
        return False

    def form_valid(self, form):
        model = form.save(commit=False)
        if hasattr(self, 'start_task') and not self.task_started(model):
            self.start_task(form, model)
        return super().form_valid(form)

class DeleteView(base.DeleteView):
    model = None
    template_name = "project/default_delete.html"
    error_template_name = 'project/default_delete_error.html'
    bdcl_remove = 0

    def post(self, request, *args, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        result = TaskResult.objects.filter(task_id=model.task_id)
        if result:
            result[0].delete()
        return super().post(request, *args, **kwargs)

class RevokeView(base.View):
    model = None
    template_name = "project/default_revoke.html"
    success_name = ''
    sleep = 1

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
        task = AsyncResult(model.task_id)
        if task.status == 'STARTED' or task.status == 'PENDING':
            task.revoke(terminate=True)
            if self.sleep > 0:
                time.sleep(self.sleep)
        return redirect(reverse(self.success_name, kwargs={'pk': model.id}))

def SearchTaskURL(task_id, task_name):
    for item in TASK_MODELS:
        if item['TaskName'] == task_name:
            cls = import_string(item['Model'])
            models = cls.objects.filter(task_id=task_id)
            if len(models) > 0:
                return reverse(item['DetailName'], kwargs={'pk': models[0].id})

def RequestUserID(task_kwargs):
    st = task_kwargs.find('request_user_id')
    if st >= 0:
        st += 17
        ed = task_kwargs[st:].find(',')
        if ed < 0:
            ed = task_kwargs[st:].find('}')
        return int(task_kwargs[st:st+ed])
    return 0

def TaskCount(worker, status, task_all):
    count = 0
    for task in task_all:
        if task.worker == worker and task.status == status:
            count += 1
    return count

def WorkerStatus(task_all):
    ins = app.control.inspect()
    stats = ins.stats()
    worker = []
    for wk in app.control.ping():
        key, value = list(wk.items())[0]
        worker.append({
            'name': key,
            'status': value,
            'concurrency': stats[key]['pool']['max-concurrency'],
            'started': TaskCount(key, 'STARTED', task_all),
            'success': TaskCount(key, 'SUCCESS', task_all),
            'failure': TaskCount(key, 'FAILURE', task_all),
            'revoked': TaskCount(key, 'REVOKED', task_all),
        })
    return worker

class TaskUserView(LoginRequiredMixin, generic.ListView):
    template_name = "project/task_user.html"
    paginate_by = 50

    def get_queryset(self):
        task_all = TaskResult.objects.all()
        user_res = []
        for res in task_all:
            if res.task_kwargs:
                uid = RequestUserID(res.task_kwargs)
                if uid == self.request.user.id:
                    url = SearchTaskURL(res.task_id, res.task_name)
                    user_res.append([res, url])
        return user_res

class TaskAllView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "project/task_all.html"
    paginate_by = 50

    def test_func(self):
        return self.request.user.is_manager

    def get_queryset(self):
        task_all = TaskResult.objects.all()
        user_res = []
        for res in task_all:
            uid = RequestUserID(res.task_kwargs)
            user = CustomUser.objects.get(id=uid)
            url = SearchTaskURL(res.task_id, res.task_name)
            user_res.append([res, user, url])
        return user_res

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    template_name = "project/task_delete.html"
    success_names = ['project:task_user', 'project:task_all']

    def test_func(self):
        if self.request.user.is_manager:
            return True
        else:
            task = TaskResult.objects.get(task_id=self.kwargs['task_id'])
            uid = RequestUserID(task.task_kwargs)
            if uid == self.request.user.id:
                return True
            else:
                return False

    def get(self, request, **kwargs):
        task = TaskResult.objects.get(task_id=kwargs['task_id'])
        params = {
            'task': task,
            'brand_name': base.BrandName(),
            'cancel_name': self.success_names[kwargs['ind']]
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        task = TaskResult.objects.get(task_id=kwargs['task_id'])
        task.delete()
        return redirect(reverse(self.success_names[kwargs['ind']]))

class TaskRevokeView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    template_name = "project/task_revoke.html"
    success_names = ['project:task_user', 'project:task_all']
    sleep = 1

    def test_func(self):
        if self.request.user.is_manager:
            return True
        else:
            task = TaskResult.objects.get(task_id=self.kwargs['task_id'])
            uid = RequestUserID(task.task_kwargs)
            if uid == self.request.user.id:
                return True
            else:
                return False

    def get(self, request, **kwargs):
        task = TaskResult.objects.get(task_id=kwargs['task_id'])
        params = {
            'task': task,
            'brand_name': base.BrandName(),
            'cancel_name': self.success_names[kwargs['ind']]
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        task = AsyncResult(kwargs['task_id'])
        if task.status == 'STARTED' or task.status == 'PENDING':
            task.revoke(terminate=True)
            if self.sleep > 0:
                time.sleep(self.sleep)
        return redirect(reverse(self.success_names[kwargs['ind']]))

class RestartDaemonView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    template_name = "project/restart_daemon.html"
    form_class = RestartDaemonForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        choices = []
        for i, daemon in enumerate(RESTART_DAEMON):
            choices.append((i, daemon['name']))
        form.fields['process'].choices = choices
        return form

    def form_valid(self, form):
        id = int(form.cleaned_data['process'])
        subprocess.call(RESTART_DAEMON[id]['call'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("project:list")
