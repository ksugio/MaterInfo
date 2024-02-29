from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from config.settings import REPOS_ROOT
from project.views import base, base_api, remote
from project.models import Project
from ..models import Repository
from ..forms import AddForm, CloneForm, NewBranchForm
from io import BytesIO
import os
import subprocess
import git

class AddView(base.FormView):
    model = Repository
    upper = Project
    form_class = AddForm
    template_name ="project/default_add.html"
    success_name = 'repository:list'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        repos = self.model.objects.filter(upper=upper)
        titles = []
        for r in repos:
            titles.append(r.title)
        form.titles = titles
        return form

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        title = form.cleaned_data['title']
        self.model.objects.create(created_by=self.request.user,
                                  updated_by=self.request.user,
                                  upper=upper, title=title)
        path = '%s/%d/%s.git' % (REPOS_ROOT, upper.id, title)
        os.makedirs(path)
        repo = git.Repo.init(path, bare=True)
        repo.index.commit('Repository created')
        return super().form_valid(form)

class CloneView(base.FormView):
    model = Repository
    upper = Project
    form_class = CloneForm
    template_name ="project/default_clone.html"
    success_name = 'repository:list'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        repos = self.model.objects.filter(upper=upper)
        titles = []
        for r in repos:
            titles.append(r.title)
        form.titles = titles
        return form

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        url = form.cleaned_data['url']
        branch = form.cleaned_data['branch']
        newname = form.cleaned_data['newname']
        if newname:
            title = newname
        else:
            title = url.split('/')[-1][:-4]
        path = '%s/%d/%s.git' % (REPOS_ROOT, upper.id, title)
        if branch:
            repo = git.Repo.clone_from(url, path, branch=branch, bare=True)
        else:
            repo = git.Repo.clone_from(url, path, bare=True)
        if repo:
            self.model.objects.create(created_by=self.request.user,
                                      updated_by=self.request.user,
                                      upper=upper, title=title)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Repository
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'repository:add'],
                  ['Clone', 'repository:clone']]

def find_hexsha(tree, hexsha):
    for item in tree:
        if item.hexsha == hexsha:
            return item, tree
        elif hasattr(item, 'trees'):
            find, parent = find_hexsha(item, hexsha)
            if find:
                return find, parent
    return None, None

class DetailView(base.DetailView):
    model = Repository
    template_name = "repository/repository_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        current_branch = self.kwargs['branch']
        url = '%s/repository/git/%d/%s.git' % (self.request._current_scheme_host, model.upper.id, model.title)
        context['url'] = url
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        tree = None
        branches = []
        for head in repo.heads:
            branches.append((head.name, 'top'))
            if head.name == current_branch:
                tree = head.commit.tree
        if not tree:
            tree = repo.head.commit.tree
        find, parent = find_hexsha(tree, self.kwargs['hexsha'])
        if not find:
            find = tree
            parent = None
        context['current_branch'] = current_branch
        context['branches'] = branches
        context['parent'] = parent
        if hasattr(find, 'trees'):
            context['trees'] = find
        else:
            context['file'] = find
            try:
                data = find.data_stream.read().decode('utf-8')
                ext = os.path.splitext(find.path)
                if ext[1] == '.md':
                    context['file_data'] = data
                else:
                    context['file_data'] = "```\n" + data + "\n```"
            except:
                context['file_data'] = 'Could not decode the file.'
        return context

class UpdateView(base.UpdateView):
    model = Repository
    fields = ('status',)
    template_name = "project/default_update.html"

# class DeleteView(base.DeleteManagerView):
#     model = Repository
#     template_name = "project/default_delete.html"
#
#     def post(self, request, *args, **kwargs):
#         model = self.model.objects.get(pk=self.kwargs['pk'])
#         path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
#         shutil.rmtree(path)
#         return super().post(request, *args, **kwargs)

class DownloadView(base.View):
    model = Repository

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        buf = BytesIO()
        repo.archive(buf, format='zip')
        response = HttpResponse(buf.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % (model.title)
        buf.close()
        return response

class BranchesView(base.DetailView):
    model = Repository
    template_name = "repository/repository_branches.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        branches = []
        for head in repo.heads:
            branches.append((head.name, 'top'))
        context['branches'] = branches
        return context

class NewBranchView(base.FormView):
    model = Repository
    form_class = NewBranchForm
    template_name ="project/default_add.html"
    title = 'New Branch'
    success_name = 'repository:branches'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        choices = []
        names = []
        for i in range(len(repo.heads)):
            choices.append((i, repo.heads[i].name))
            names.append(repo.heads[i].name)
        form.fields['source'].choices = choices
        form.names = names
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['title'] = model.title + ' - ' + self.title
        context['btn_title'] = 'New'
        return context

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        name = form.cleaned_data['name']
        sid = int(form.cleaned_data['source'])
        source = form.fields['source'].choices[sid][1]
        repo.git.branch(name, source)
        return super().form_valid(form)

class DeleteBranchView(base.View):
    model = Repository
    template_name = 'repository/branch_delete.html'

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model),
            'branch': kwargs['branch']
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        path = '%s/%d/%s.git' % (REPOS_ROOT, model.upper.id, model.title)
        repo = git.Repo(path)
        branch = kwargs['branch']
        repo.git.branch(d=branch)
        return redirect(reverse('repository:branches', kwargs={'pk': model.id}))

