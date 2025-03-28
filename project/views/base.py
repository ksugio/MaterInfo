from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.utils.module_loading import import_string
from django.db.models import Q
from io import BytesIO, StringIO
from config.settings import BRAND_NAME, MEDIA_ACCEL_REDIRECT, FILE_ITEMS
import datetime
import os
import mimetypes
import urllib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def ProjectModel(model):
    while True:
        if model.upper:
            model = model.upper
        else:
            break
    return model

def ProjectMember(model):
    return ProjectModel(model).member.all()

class Link:
    def __init__(self, title, url):
        self.title = title
        self.url = url

def BreadcrumbList(model):
    list = []
    while True:
        if model.upper:
            if hasattr(model, 'get_list_url'):
                list.append(Link(model.__class__.__name__, model.get_list_url()))
            if hasattr(model, 'get_detail_url'):
                list.append(Link(model.upper.title, model.upper.get_detail_url()))
            model = model.upper
        else:
            if hasattr(model, 'get_list_url'):
                list.append(Link(model.__class__.__name__, model.get_list_url()))
            break
    list.reverse()
    return list

def BreadcrumbDetail(model):
    list = BreadcrumbList(model)
    if hasattr(model, 'get_detail_url'):
        list.append(Link(model.title, model.get_detail_url()))
    return list

def NavigationList(navigation, pk):
    nav_list = []
    for item in navigation:
        if len(item) == 2:
            nav_list.append(Link(item[0], reverse(item[1], kwargs={'pk': pk})))
        elif len(item) == 3:
            kwargs = {'pk': pk}
            kwargs.update(item[2])
            nav_list.append(Link(item[0], reverse(item[1], kwargs=kwargs)))
    return nav_list

def DateToday():
    today = datetime.date.today()
    return '{0:%Y%m%d}'.format(today)

def Entity(models):
    entity = []
    for model in models:
        entity.append(model.entity())
    return entity

def DataFrame2UploadedFile(df, fname):
    buf = BytesIO()
    df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
    file = InMemoryUploadedFile(ContentFile(buf.getvalue()), None, fname, 'text/csv', None, None)
    buf.close()
    return file

def BrandName():
    return BRAND_NAME

class AddView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = None
    upper = None
    template_name = "project/default_add.html"
    title = ''
    bdcl_remove = 0

    def test_func(self):
        upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(upper)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        if self.title:
            context['title'] = self.title
        else:
            context['title'] = self.model.__name__ + ' Add'
        if self.upper is not None:
            upper = self.upper.objects.get(pk=self.kwargs['pk'])
            if self.bdcl_remove > 0:
                context['breadcrumb_list'] = BreadcrumbDetail(upper)[:-self.bdcl_remove]
                if callable(upper.title):
                    uptitle = upper.title()
                else:
                    uptitle = upper.title
                context['title'] = uptitle + ' : ' + context['title']
            else:
                context['breadcrumb_list'] = BreadcrumbDetail(upper)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        if self.upper is not None:
            model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.created_by = self.request.user
        model.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if hasattr(self.object, 'get_list_url'):
            return self.object.get_list_url()
        elif hasattr(self.object, 'get_detail_url'):
            return self.object.get_detail_url()

class ListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = None
    upper = None
    template_name = "project/default_list.html"
    navigation = []
    title = ''

    def test_func(self):
        upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(upper)

    def get_queryset(self):
        if self.upper is not None:
            upper = self.upper.objects.get(pk=self.kwargs['pk'])
            if hasattr(self.model, 'created_by'):
                return self.model.objects.filter(upper=upper).order_by('-created_at')
            else:
                return self.model.objects.filter(upper=upper)
        else:
            if hasattr(self.model, 'created_by'):
                return self.model.objects.all().order_by('-created_at')
            else:
                return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        if self.title:
            context['title'] = self.title
        else:
            context['title'] = self.model.__name__
        if self.upper is not None:
            upper = self.upper.objects.get(pk=self.kwargs['pk'])
            context['breadcrumb_list'] = BreadcrumbDetail(upper)
            if len(self.navigation) > 0:
                context['navigation_list'] = NavigationList(self.navigation, upper.id)
        return context

class DetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = None
    template_name = "project/default_detail.html"
    navigation = []

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['breadcrumb_list'] = BreadcrumbList(model)
        if len(self.navigation) > 0:
            context['navigation_list'] = NavigationList(self.navigation, model.id)
        return context

class UpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = None
    template_name = "project/default_update.html"
    bdcl_remove = 0

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.bdcl_remove > 0:
            context['breadcrumb_list'] = BreadcrumbList(model)[:-self.bdcl_remove]
        else:
            context['breadcrumb_list'] = BreadcrumbList(model)
        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_detail_url()

class DeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = None
    template_name = "project/default_delete.html"
    error_template_name = 'project/default_delete_error.html'
    bdcl_remove = 0

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if self.bdcl_remove > 0:
            context['breadcrumb_list'] = BreadcrumbList(model)[:-self.bdcl_remove]
        else:
            context['breadcrumb_list'] = BreadcrumbList(model)
        return context

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        except:
            params = {
                'object': self.object,
                'brand_name': BrandName(),
                'breadcrumb_list': BreadcrumbList(self.object),
            }
            return render(request, self.error_template_name, params)

    def get_success_url(self):
        if hasattr(self.object, 'get_list_url'):
            return self.object.get_list_url()
        elif hasattr(self.object, 'get_detail_url'):
            return self.object.get_detail_url()

class DeleteAliasView(DeleteView):
    model = None
    template_name = "project/default_delete_alias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['aliases'] = self.model.objects.filter(alias=model.id)
        return context

    def post(self, request, *args, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        aliases = self.model.objects.filter(alias=model.id)
        for alias in aliases:
            alias.title = alias.title[0:-7] + '(Unalias)'
            alias.alias = None
            alias.save()
        return super().post(request, *args, **kwargs)

class DeleteManagerView(DeleteView):
    model = None
    template_name = "project/default_delete.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model) and self.request.user.is_manager

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class FormView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    model = None
    upper = None
    form_class = None
    template_name = ""
    title = ''
    success_name = ''
    bdcl_remove = 0

    def test_func(self):
        if self.upper:
            upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(upper)
        else:
            model = get_object_or_404(self.model, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        if self.title:
            context['title'] = self.title
        else:
            context['title'] = self.model.__name__
        if 'pk' in self.kwargs:
            if self.upper:
                upper = self.upper.objects.get(pk=self.kwargs['pk'])
                if self.bdcl_remove > 0:
                    context['breadcrumb_list'] = BreadcrumbDetail(upper)[:-self.bdcl_remove]
                else:
                    context['breadcrumb_list'] = BreadcrumbDetail(upper)
            else:
                model = self.model.objects.get(pk=self.kwargs['pk'])
                if self.bdcl_remove > 0:
                    context['breadcrumb_list'] = BreadcrumbList(model)[:-self.bdcl_remove]
                else:
                    context['breadcrumb_list'] = BreadcrumbList(model)
        return context

    def get_success_url(self):
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk']})

class TemplateView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    model = None
    upper = None
    template_name = "project/default_detail.html"
    bdcl_remove = 0

    def test_func(self):
        if self.upper:
            upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(upper)
        else:
            model = get_object_or_404(self.model, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        context['title'] = self.model.__name__
        if 'pk' in self.kwargs:
            if self.upper:
                upper = self.upper.objects.get(pk=self.kwargs['pk'])
                if self.bdcl_remove > 0:
                    context['breadcrumb_list'] = BreadcrumbDetail(upper)[:-self.bdcl_remove]
                else:
                    context['breadcrumb_list'] = BreadcrumbDetail(upper)
            else:
                model = self.model.objects.get(pk=self.kwargs['pk'])
                if self.bdcl_remove > 0:
                    context['breadcrumb_list'] = BreadcrumbList(model)[:-self.bdcl_remove]
                else:
                    context['breadcrumb_list'] = BreadcrumbList(model)
        return context

class View(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    model = None
    upper = None

    def test_func(self):
        if self.upper:
            upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(upper)
        else:
            model = get_object_or_404(self.model, id=self.kwargs['pk'])
            return self.request.user in ProjectMember(model)

    def brandName(self):
        return BrandName()

    def breadcrumbList(self, model, bdcl_remove=0):
        if bdcl_remove > 0:
            return BreadcrumbList(model)[:-bdcl_remove]
        else:
            return BreadcrumbList(model)

    def breadcrumbDetail(self, model, bdcl_remove=0):
        if bdcl_remove > 0:
            return BreadcrumbDetail(model)[:-bdcl_remove]
        else:
            return BreadcrumbDetail(model)

class MDEditView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    model = None
    text_field = ''
    template_name = "project/default_mdedit.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['object'] = model
        context['breadcrumb_list'] = BreadcrumbList(model)
        context['initial_text'] = getattr(model, self.text_field)
        context['text_field'] = self.text_field
        return context

class FileView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    model = None
    attachment = False
    field = 'file'
    use_unique = False
    utf8_filename = False

    def test_func(self):
        if self.use_unique:
            model = get_object_or_404(self.model, unique=self.kwargs['unique'])
        else:
            model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get_file(self, **kwargs):
        if self.use_unique:
            model = self.model.objects.get(unique=kwargs['unique'])
        else:
            model = self.model.objects.get(pk=kwargs['pk'])
        file = getattr(model, self.field)
        filename = os.path.basename(file.name)
        return file, filename

    def get(self, request, **kwargs):
        file, filename = self.get_file(**kwargs)
        if MEDIA_ACCEL_REDIRECT:
            response = HttpResponse()
            response['X-Accel-Redirect'] = "/media/{0}".format(file.name)
        else:
            response = FileResponse(file.open("rb"))
        response["Content-Type"] = mimetypes.guess_type(filename)[0]
        if self.attachment:
            if self.utf8_filename:
                fn = urllib.parse.quote(filename)
                response["Content-Disposition"] = "attachment; filename='{0}'; filename*=UTF-8''{1}".format(fn, fn)
            else:
                response["Content-Disposition"] = "attachment; filename={0}".format(filename)
        else:
            if self.utf8_filename:
                fn = urllib.parse.quote(filename)
                response["Content-Disposition"] = "inline; filename='{0}'; filename*=UTF-8''{1}".format(fn, fn)
            else:
                response["Content-Disposition"] = "inline; filename={0}".format(filename)
        return response

class PlotView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    model = None
    methods = 'plot'

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        attr = getattr(model, self.methods)
        if callable(attr):
            kwargs['request_host'] = request._current_scheme_host
            kwargs['request_cookies'] = request.COOKIES
            figure = attr(**kwargs)
        buf = BytesIO()
        if figure is not None:
            figure.savefig(buf, format='svg', bbox_inches='tight')
        else:
            plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class TableView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    model = None
    methods = 'disp_table'
    template_name = "project/default_table.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        attr = getattr(model, self.methods)
        if callable(attr):
            kwargs['request_host'] = request._current_scheme_host
            kwargs['request_cookies'] = request.COOKIES
            df = attr(**kwargs)
            if df is not None:
                buf = StringIO()
                df.to_html(buf)
                table = buf.getvalue()
                buf.close()
                return render(request, self.template_name, {'table' : table})
        return render(request, self.template_name)

class ImageView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    model = None
    methods = 'get_image'

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model)

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        attr = getattr(model, self.methods)
        if callable(attr):
            kwargs['request_host'] = request._current_scheme_host
            kwargs['request_cookies'] = request.COOKIES
            pilimg = attr(**kwargs)
            if pilimg is None:
                response = HttpResponse('Cannot read image file.')
            else:
                buf = BytesIO()
                pilimg.save(buf, format='png')
                response = HttpResponse(buf.getvalue(), content_type='image/png')
                buf.close()
            return response

class Search:
    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(title__icontains=text) |
                  Q(note__icontains=text), cond)
        return q

    def get_models(self, upper):
        return self.model.objects.filter(upper=upper)

    def search(self, upper, **kwargs):
        texts = []
        for text in kwargs['string'].strip().split(' '):
            if text:
                texts.append(text)
        if  int(kwargs['condition']) == 1:
            cond = Q.AND
        else:
            cond = Q.OR
        q = self.search_queries(texts, cond)
        models = self.get_models(upper)
        results = []
        for model in models.filter(q):
            results.append(model)
        if hasattr(self, 'check_child'):
            for model in models.filter(~q):
                if self.check_child(model, texts, cond):
                    results.append(model)
        if hasattr(self, 'lower_items') and kwargs['lower']:
            results.extend(self.search_lower(upper, **kwargs))
        return results

    def search_lower(self, upper, **kwargs):
        results = []
        models = self.get_models(upper)
        for model in models:
            for item in self.lower_items:
                if 'Search' in item:
                    cls = import_string(item['Search'])
                    results.extend(cls().search(model, **kwargs))
        return results

class SearchView(FormView, Search):
    model = None
    upper = None
    form_class = None
    template_name = "project/default_search.html"
    title = ''
    session_name = ''
    back_name = ''

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.session_name in self.request.session:
            form_value = self.request.session[self.session_name]
            form.fields['string'].initial = form_value[0]
            form.fields['condition'].initial = form_value[1]
            form.fields['lower'].initial = form_value[2]
            form.fields['order'].initial = form_value[3]
        return form

    @staticmethod
    def sort_key(value):
        if hasattr(value, 'updated_at'):
            return value.updated_at
        elif hasattr(value, 'created_at'):
            return value.created_at

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.upper:
            upper = self.upper.objects.get(pk=self.kwargs['pk'])
            context['back_url'] = reverse(self.back_name, kwargs={'pk': upper.id})
        else:
            upper = None
            context['back_url'] = reverse(self.back_name)
        if self.session_name in self.request.session:
            form_value = self.request.session[self.session_name]
            results = self.search(upper, string=form_value[0],
                                  condition=form_value[1],
                                  lower=form_value[2])
            if int(form_value[3]) == 0:
                results = sorted(results, key=SearchView.sort_key, reverse=True)
            elif int(form_value[3]) == 1:
                results = sorted(results, key=SearchView.sort_key, reverse=False)
            context['results'] = results
        return context

    def post(self, request, *args, **kwargs):
        form_value = [
            self.request.POST.get('string', None),
            self.request.POST.get('condition', None),
            self.request.POST.get('lower', None),
            self.request.POST.get('order', None)
        ]
        request.session[self.session_name] = form_value
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)

class MoveView(UpdateView):
    model = None
    fields = ('upper',)
    template_name = "project/default_update.html"
    bdcl_remove = 0

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        project = ProjectModel(model)
        form = super().get_form(form_class=form_class)
        newchoices = []
        for choice in form.fields['upper'].choices:
            if hasattr(choice[0], 'instance'):
                if project == ProjectModel(choice[0].instance):
                    newchoices.append(choice)
        form.fields['upper'].choices = newchoices
        return form

class MoveManagerView(MoveView):
    model = None
    fields = ('upper',)
    template_name = "project/default_update.html"
    bdcl_remove = 0

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in ProjectMember(model) and self.request.user.is_manager

class FileSearch:
    def model_search(self, url):
        for dic in FILE_ITEMS:
            lurl = url.split('/')
            path = reverse(dic['FileName'], args=range(1))
            lpath = path.split('/')
            if lurl[:-2] == lpath[:-2] and lurl[-1] == lpath[-1]:
                cls = import_string(dic['Model'])
                model = cls.objects.filter(unique=lurl[-2])
                if model:
                    return model[0], dic
        return None, None

    def file_search(self, url):
        model, dic = self.model_search(url)
        if model:
            return getattr(model, dic['FileField'])
        else:
            return None

    def detail_search(self, url):
        model, dic = self.model_search(url)
        if model and 'DetailName' in dic:
            return reverse(dic['DetailName'], kwargs={'pk': model.id})
        else:
            return None
