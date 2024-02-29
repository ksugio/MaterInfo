from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from project.views import base, base_api, remote
from project.models import Project
from .models import Comment, Response
from .forms import CommentForm, ResponseForm
from .serializer import CommentSerializer, ResponseSerializer

class AddView(base.FormView):
    model = Comment
    upper = Project
    form_class = CommentForm
    template_name = "project/default_add.html"
    title = 'Comment Add'
    success_name = 'comment:list'

    def send_mail(self, model):
        subject = '[%s:Comment] %s' % (base.BrandName(), model.title)
        message = 'New comment was posted by ' + self.request.user.username + \
                  '\n\nProject: ' + model.upper.title + '\nComment:\n' + model.comment + \
                  '\n\nDo not reply to this mail. Response from '+ \
                  self.request._current_scheme_host + \
                  reverse('comment:detail', kwargs={'pk': model.id})
        addrs = []
        for member in model.upper.member.all():
            if member.email:
                addrs.append(member.email)
        if addrs:
            send_mail(subject, message, DEFAULT_FROM_EMAIL, addrs)

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        title = form.cleaned_data['title']
        comment = form.cleaned_data['comment']
        file = form.cleaned_data['file']
        sendemail = form.cleaned_data['sendemail']
        model = self.model.objects.create(created_by=self.request.user, upper=upper,
                                          title=title, comment=comment, file=file)
        if sendemail:
            self.send_mail(model)
        return super().form_valid(form)

class ListView(base.ListView):
    model = Comment
    upper = Project
    template_name = "comment/comment_list.html"
    navigation = [['Add', 'comment:add'],]
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_set = []
        for comment in context['comment_list']:
            responses = Response.objects.filter(upper=comment).order_by('created_at')
            comment_set.append((comment, responses))
        context['comment_set'] = comment_set
        return context

class DetailView(base.DetailView):
    model = Comment
    template_name = "comment/comment_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['responses'] = Response.objects.filter(upper=model).order_by('created_at')
        return context

class FileView(base.FileView):
    model = Comment
    attachment = False

class ResponseView(base.FormView):
    model = Response
    upper = Comment
    form_class = ResponseForm
    template_name = "comment/comment_response.html"
    title = ''
    success_name = 'comment:detail'
    bdcl_remove = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        context['comment'] = upper
        return context

    def send_mail(self, model):
        subject = '[%s:Response] %s' % (base.BrandName(), model.upper.title)
        message = 'New response was posted by ' + self.request.user.username + \
                  '\n\nProject: ' + model.upper.upper.title + '\nTitle: ' + model.upper.title + \
                  '\nComment:\n' + model.upper.comment + '\nResponse:\n' + model.response + \
                  '\n\nDo not reply to this mail. Response from '+ \
                  self.request._current_scheme_host + \
                  reverse('comment:detail', kwargs={'pk': model.upper.id})
        addrs = []
        for member in model.upper.upper.member.all():
            if member.email:
                addrs.append(member.email)
        if addrs:
            send_mail(subject, message, DEFAULT_FROM_EMAIL, addrs)

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        response = form.cleaned_data['response']
        file = form.cleaned_data['file']
        sendemail = form.cleaned_data['sendemail']
        model = self.model.objects.create(created_by=self.request.user, upper=upper,
                                          response=response, file=file)
        if sendemail:
            self.send_mail(model)
        return super().form_valid(form)

    def get_success_url(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return reverse(self.success_name, kwargs={'pk': upper.id})

class ResponseFileView(base.FileView):
    model = Response
    attachment = False

class CommentSearch(base.Search):
    model = Comment

    def search_queries(self, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(title__icontains=text) |
                  Q(comment__icontains=text), cond)
        return q

    def check_child(self, upper, texts, cond):
        q = Q()
        for text in texts:
            q.add(Q(response__icontains=text), cond)
        response = Response.objects.filter(upper=upper).filter(q)
        return response

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(created_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Comment
    serializer_class = CommentSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Comment
    serializer_class = CommentSerializer

class FileAPIView(base_api.FileAPIView):
    model = Comment
    attachment = False

class ResponseAddAPIView(base_api.AddAPIView):
    upper = Comment
    serializer_class = ResponseSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(created_by=self.request.user, upper=upper)

class ResponseListAPIView(base_api.ListAPIView):
    upper = Comment
    model = Response
    serializer_class = ResponseSerializer

class ResponseRetrieveAPIView(base_api.RetrieveAPIView):
    model = Response
    serializer_class = ResponseSerializer

class ResponseFileAPIView(base_api.FileAPIView):
    model = Response
    attachment = False

class ResponseRemote(remote.FileRemote):
    model = Response
    add_name = 'comment:api_response_add'
    list_name = 'comment:api_response_list'
    retrieve_name = 'comment:api_response_retrieve'
    file_fields_names = [('file', 'comment:api_response_file')]
    serializer_class = ResponseSerializer

class CommentRemote(remote.FileRemote):
    model = Comment
    add_name = 'comment:api_add'
    list_name = 'comment:api_list'
    retrieve_name = 'comment:api_retrieve'
    file_fields_names = [('file', 'comment:api_file')]
    serializer_class = CommentSerializer
    child_remote = [ResponseRemote]
