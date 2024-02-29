from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from project.views import base
from ..models import Public, PublicMenu
from ..serializer import PublicMenuSerializer

class AddView(base.AddView):
    upper = Public
    model = PublicMenu
    fields = ('title', 'url', 'order')
    template_name = "project/default_add.html"

    def test_func(self):
         return self.request.user.is_manager

class ListView(base.ListView):
    upper = Public
    model = PublicMenu
    template_name = "public/menu_list.html"
    navigation = [['Add', 'public:menu_add'], ]

    def test_func(self):
         return self.request.user.is_manager

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper).order_by('order')

class UpdateView(base.UpdateView):
    model = PublicMenu
    fields = ('title', 'url', 'order')
    template_name = "project/default_update.html"

    def test_func(self):
        return self.request.user.is_manager

class DeleteView(base.DeleteView):
    model = PublicMenu
    template_name = "project/default_delete.html"

    def test_func(self):
        return self.request.user.is_manager

# API
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class AddAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    upper = Public
    serializer_class = PublicMenuSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicMenu
    upper = Public
    serializer_class = PublicMenuSerializer

    def get_queryset(self):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        return self.model.objects.filter(upper=upper)

class RetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicMenu
    serializer_class = PublicMenuSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class UpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicMenu
    serializer_class = PublicMenuSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()

class DeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsManager)
    model = PublicMenu
    serializer_class = PublicMenuSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return self.model.objects.all()
