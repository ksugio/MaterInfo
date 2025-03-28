from django.views import generic
from django.http import Http404, HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from project.views import base
from article.models import Article
from ..models import Public, PublicArticle
from ..serializer import PublicArticleSerializer
from io import BytesIO

class AddView(base.AddView):
    upper = Public
    model = PublicArticle
    fields = ('article',)
    template_name = "project/default_add.html"

    def test_func(self):
         return self.request.user.is_manager

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        articles = Article.objects.filter(public=True, type=0)
        candidate = []
        for article in articles:
            candidate.append((article.id, article.title))
        form.fields['article'].choices = candidate
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.posted_by = self.request.user
        return super().form_valid(form)

class ListView(base.ListView):
    upper = Public
    model = PublicArticle
    template_name = "public/article_list.html"
    navigation = [['Add', 'public:article_add'],]

    def test_func(self):
         return self.request.user.is_manager

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper).order_by('-posted_at')

class DetailView(base.DetailView):
    model = PublicArticle
    template_name = "public/article_detail.html"

    def test_func(self):
         return self.request.user.is_manager

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        article_list = self.model.objects.filter(upper=model.upper).order_by('-posted_at')
        ind = list(article_list).index(model)
        if ind > 0:
            context['prev_article'] = article_list[ind-1]
        else:
            context['prev_article'] = None
        if ind < len(article_list) - 1:
            context['next_article'] = article_list[ind+1]
        else:
            context['next_article'] = None
        context['style_css'] = model.upper.style_css
        context['header'] = { 'title': model.upper.title,
                              'note': model.upper.note,
                              'color': model.upper.header_color,
                              'image': model.upper.header_image,
                              'url': model.upper.get_header_image_url()}
        return context

class UpdateView(base.UpdateView):
    model = PublicArticle
    fields = ('article',)
    template_name = "public/article_update.html"

    def test_func(self):
        return self.request.user.is_manager

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        articles = Article.objects.filter(public=True, type=0)
        candidate = []
        for article in articles:
            candidate.append((article.id, article.title))
        form.fields['article'].choices = candidate
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        model.posted_by = self.request.user
        return super().form_valid(form)

class DeleteView(base.DeleteView):
    model = PublicArticle
    template_name = "project/default_delete.html"

    def test_func(self):
        return self.request.user.is_manager

def Release(request, model, header, changes):
    article_list = PublicArticle.objects.filter(upper=model.upper).order_by('-posted_at')
    ind = list(article_list).index(model)
    if ind > 0:
        prev_article = article_list[ind - 1]
    else:
        prev_article = None
    if ind < len(article_list) - 1:
        next_article = article_list[ind + 1]
    else:
        next_article = None
    modify, changes = model.modify_text(request, changes)
    params = {
        'object': model,
        'prev_article': prev_article,
        'next_article': next_article,
        'style_css': model.upper.style_css,
        'header': header,
        'public_mode': True,
        'modify_text': modify
    }
    html = render(request, "public/article_detail.html", params)
    buf = BytesIO()
    buf.write(html.content)
    filename = '%s.html' % model.__class__.__name__
    model.file.save(filename, buf)
    buf.close()
    return changes

class HomeView(generic.View):
    model = PublicArticle

    def get(self, request, **kwargs):
        try:
            article = self.model.objects.get(pk=kwargs['pk'])
        except:
            raise Http404("Page not found")
        if not article.file:
            raise Http404("Page not found")
        with article.file.open(mode='rb') as f:
            html = f.read()
            return HttpResponse(html)

# API
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    upper = Public
    serializer_class = PublicArticleSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(posted_by=self.request.user, upper=upper)

class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicArticle
    upper = Public
    serializer_class = PublicArticleSerializer

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper)

class RetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicArticle
    serializer_class = PublicArticleSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class UpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicArticle
    serializer_class = PublicArticleSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class DeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicArticle
    serializer_class = PublicArticleSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()
