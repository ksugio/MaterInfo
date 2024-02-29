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

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsMemberUp)
    upper = None
    serializer_class = None

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(created_by=self.request.user, updated_by=self.request.user, upper=upper)

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

#
# Good
# class GoodAPIView(views.APIView):
#     permission_classes = (IsAuthenticated, IsMember)
#     model = None
#
#     def get(self, request, pk=None):
#         object = get_object_or_404(self.model, pk=self.kwargs['pk'])
#         url_ = object.get_detail_url()
#         status = request.GET.getlist('status')
#         print(status)
#         status = bool(int(status[0]))
#         status = True
#         user = self.request.user
#         if user in object.good.all():
#             if not (status):
#                 good = True
#             else:
#                 object.good.remove(user)
#                 good = False
#         else:
#             if not (status):
#                 good = False
#             else:
#                 object.good.add(user)
#                 good = True
#         data = {
#             "good": good,
#         }
#         return Response(data)