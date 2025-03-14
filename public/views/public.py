from django.views import generic
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from project.views import base
from ..models import Public, PublicArticle, PublicMenu, PublicFile, RandomString
from ..serializer import PublicSerializer
from .article import Release
from io import BytesIO

class AddView(base.AddView):
    model = Public
    fields = ('title', 'path', 'note', 'header_color', 'header_image', 'style_css')
    template_name = "project/default_add.html"

    def test_func(self):
         return self.request.user.is_manager

class ListView(base.ListView):
    model = Public
    template_name = "public/public_list.html"

    def test_func(self):
         return self.request.user.is_manager

class DetailView(base.DetailView):
    model = Public
    template_name = "public/public_detail.html"

    def test_func(self):
         return self.request.user.is_manager

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['article_list'] = PublicArticle.objects.filter(upper=model).order_by('-posted_at')
        context['menu_list'] = PublicMenu.objects.filter(upper=model).order_by('order')
        context['style_css'] = model.style_css
        context['header'] = { 'title': model.title,
                              'note': model.note,
                              'color': model.header_color,
                              'image': model.header_image,
                              'url': model.get_header_image_url() }
        return context

class UpdateView(base.UpdateView):
    model = Public
    fields = ('title', 'path', 'note', 'header_color', 'header_image', 'style_css')
    template_name = "project/default_update.html"

    def test_func(self):
        return self.request.user.is_manager

class ReleaseView(base.View):
    model = Public
    template_name = "public/public_release.html"
    success_name = "public:home"

    def test_func(self):
        return self.request.user.is_manager

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        params = {
            'object': model,
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def update_files(self, model):
        items = PublicFile.objects.filter(upper=model)
        for item in items:
            if not item.header or model.header_image:
                item.set_file(self.request)
            item.save()

    def header_params(self, model):
        items = PublicFile.objects.filter(url=model.get_header_image_url())
        if items:
            header_image = items[0]
        elif model.header_image:
            content = model.header_image.read()
            file = InMemoryUploadedFile(ContentFile(content), None,
                                        model.header_image.name,None,
                                        len(content), None)
            header_image = PublicFile.objects.create(upper=model, updated_by=self.request.user,
                                                     url=model.get_header_image_url(),
                                                     key=RandomString(), file=file, header=True)
        else:
            header_image = None
        params = {
            'title': model.title,
            'note': model.note,
            'color': model.header_color,
            'image': model.header_image
        }
        if header_image:
            params['url'] = '/public/file/{0}'.format(header_image.key)
        return params

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        article = PublicArticle.objects.filter(upper=model).order_by('-posted_at')
        menu = PublicMenu.objects.filter(upper=model).order_by('order')
        self.update_files(model)
        header = self.header_params(model)
        params = {
            'object': model,
            'article_list': article,
            'menu_list': menu,
            'style_css': model.style_css,
            'header' : header,
            'public_mode': True
        }
        html = render(self.request, "public/public_detail.html", params)
        buf = BytesIO()
        buf.write(html.content)
        filename = '%s.html' % model.__class__.__name__
        model.file.save(filename, buf)
        buf.close()
        changes = []
        for item in article:
            changes = Release(self.request, item, header, changes)
        for change in changes:
            if change['create']:
                PublicFile.objects.create(upper=model, updated_by=self.request.user,
                                          url=change['url'], key=change['key'],
                                          file=change['file'])
        return redirect(reverse(self.success_name, kwargs={'path': model.path}))

class DeleteView(base.DeleteView):
    model = Public
    template_name = "project/default_delete.html"

    def test_func(self):
        return self.request.user.is_manager

class HeaderImageView(base.FileView):
    model = Public
    attachment = False
    field = 'header_image'

    def test_func(self):
        return self.request.user.is_manager

class HomeView(generic.View):
    model = Public

    def get(self, request, **kwargs):
        try:
            public = self.model.objects.get(path=kwargs['path'])
        except:
            raise Http404("Page not found")
        if not public.file:
            raise Http404("Page not found")
        with public.file.open(mode='rb') as f:
            html = f.read()
            return HttpResponse(html)

# API
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    serializer_class = PublicSerializer

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = Public
    serializer_class = PublicSerializer

    def get_queryset(self):
        return self.model.objects.all()

class RetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = Public
    serializer_class = PublicSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class UpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = Public
    serializer_class = PublicSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class DeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    model = Public
    serializer_class = PublicSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()
