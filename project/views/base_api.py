from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, BasePermission
from config.settings import MEDIA_ACCEL_REDIRECT, USE_LOCAL_HOST
from .base import ProjectMember
import os
import mimetypes

class IsMemberUp(BasePermission):
    def has_permission(self, request, view):
        upper = get_object_or_404(view.upper, id=view.kwargs['pk'])
        return request.user in ProjectMember(upper)

class IsMember(BasePermission):
    def has_permission(self, request, view):
        model = get_object_or_404(view.model, id=view.kwargs['pk'])
        return request.user in ProjectMember(model)

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class IsManagerOrCreateUser(BasePermission):
    def has_permission(self, request, view):
        model = get_object_or_404(view.model, id=view.kwargs['pk'])
        return request.user == model.created_by or request.user.is_manager

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsMemberUp)
    upper = None
    serializer_class = None

    def perform_create(self, serializer):
        option = {}
        if hasattr(self.serializer_class.Meta.model, 'created_by'):
            option['created_by'] = self.request.user
        if hasattr(self.serializer_class.Meta.model, 'updated_by'):
            option['updated_by'] = self.request.user
        if hasattr(self.serializer_class.Meta.model, 'upper'):
            option['upper'] = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(**option)

class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsMemberUp)
    upper = None
    model = None
    serializer_class = None

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper)

class RetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsMember)
    model = None
    serializer_class = None
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class UpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsMember)
    model = None
    serializer_class = None
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class DeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsMember)
    model = None
    serializer_class = None
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class APIView(views.APIView):
    permission_classes = (IsAuthenticated, IsMember)
    model = None

class FileAPIView(views.APIView):
    permission_classes = (IsAuthenticated, IsMember)
    model = None
    attachment = False
    field = 'file'

    def is_localhost(self, request):
        if USE_LOCAL_HOST['check']:
            host = request._current_scheme_host
            localhost = USE_LOCAL_HOST['localhost']
            if host == localhost:
                return True
        return False

    def get(self, request, pk):
        model = self.model.objects.get(pk=pk)
        file = getattr(model, self.field)
        basename = os.path.basename(file.name)
        if MEDIA_ACCEL_REDIRECT and not self.is_localhost(request):
            response = HttpResponse()
            response["Content-Type"] = mimetypes.guess_type(basename)[0]
            if self.attachment:
                response["Content-Disposition"] = "attachment; filename={0}".format(basename)
            else:
                response["Content-Disposition"] = "inline; filename={0}".format(basename)
            response['X-Accel-Redirect'] = "/media/{0}".format(file.name)
            return response
        else:
            return FileResponse(file.open("rb"), as_attachment=self.attachment, filename=basename)
