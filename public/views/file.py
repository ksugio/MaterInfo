from django.views import generic
from django.http import HttpResponse, FileResponse, Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from config.settings import MEDIA_ROOT, MEDIA_ACCEL_REDIRECT
from project.views import base
from ..models import Public, PublicFile, RandomString
from ..serializer import PublicFileSerializer
import os
import mimetypes

class AddView(base.AddView):
    upper = Public
    model = PublicFile
    fields = ('url',)
    template_name = "project/default_add.html"

    def test_func(self):
         return self.request.user.is_manager

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.key = RandomString()
        model.updated_by = self.request.user
        model.set_file(self.request)
        return super().form_valid(form)

class ListView(base.ListView):
    upper = Public
    model = PublicFile
    template_name = "public/file_list.html"
    navigation = [['Add', 'public:file_add'],]

    def test_func(self):
         return self.request.user.is_manager

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper).order_by('-updated_at')

class UpdateView(base.UpdateView):
    model = PublicFile
    fields = ('url', 'key')
    template_name = "project/default_update.html"

    def test_func(self):
        return self.request.user.is_manager

    def form_valid(self, form):
        model = form.save(commit=False)
        model.key = RandomString()
        model.updated_by = self.request.user
        model.set_file(self.request)
        return super().form_valid(form)

class DeleteView(base.DeleteView):
    model = PublicFile
    template_name = "project/default_delete.html"

    def test_func(self):
        return self.request.user.is_manager

class FileView(generic.View):
    model = PublicFile

    def get(self, request, **kwargs):
        model = self.model.objects.filter(key=kwargs['key'])
        if not model:
            raise Http404
        model = model[0]
        basename = os.path.basename(model.file.name)
        if MEDIA_ACCEL_REDIRECT:
            response = HttpResponse()
            response["Content-Type"] = mimetypes.guess_type(basename)[0]
            response["Content-Disposition"] = "inline; filename={0}".format(basename)
            response['X-Accel-Redirect'] = "/media/{0}".format(model.file.name)
            return response
        else:
            return FileResponse(model.file.open('rb'),
                                as_attachment=False, filename=basename)

# API
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    upper = Public
    serializer_class = PublicFileSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicFile
    upper = Public
    serializer_class = PublicFileSerializer

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper)

class RetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicFile
    serializer_class = PublicFileSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class UpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicFile
    serializer_class = PublicFileSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class DeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicFile
    serializer_class = PublicFileSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()
