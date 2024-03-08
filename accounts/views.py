from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import views as auth
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from config import settings
from project.models import CreateUserProject
from project.views.base import BrandName
from .models import CustomUser
from .forms import UserAddForm, UserUploadForm, UserCloneForm, ProfileUpdateForm, PasswordForm
from .serializer import UserSerializer
from .ldap import LDAPUpdateUser, LDAPChangePassword
import io
import csv
import datetime
import requests

UserUploadDateFormat = '%B %d %Y'

class LoginView(auth.LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        context['email_active'] = settings.EMAIL_ACTIVE
        return context

class LogoutView(auth.LogoutView):
    template_name = 'accounts/logout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class PasswordChangeView(LoginRequiredMixin, auth.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if response.status_code == 302:
            if settings.LDAP_SERVER['USE'] and settings.LDAP_SERVER['UPDATE_SERVER']:
                LDAPChangePassword(self.request.user.username,
                                   form.cleaned_data['old_password'],
                                   form.cleaned_data['new_password1'])
        return response

class PasswordChangeDoneView(LoginRequiredMixin, auth.PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class PasswordReset(auth.PasswordResetView):
    subject_template_name = 'accounts/mail_template/password_reset/subject.txt'
    email_template_name = 'accounts/mail_template/password_reset/message.txt'
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class PasswordResetDone(auth.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class PasswordResetConfirm(auth.PasswordResetConfirmView):
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'accounts/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class PasswordResetComplete(auth.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class ProfileUpdateView(LoginRequiredMixin, generic.FormView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.request.user.id)
        form = super().get_form(form_class=form_class)
        form.fields['first_name'].initial = model.first_name
        form.fields['last_name'].initial = model.last_name
        form.fields['email'].initial = model.email
        form.fields['idnumber'].initial = model.idnumber
        form.fields['fullname'].initial = model.fullname
        form.fields['postalcode'].initial = model.postalcode
        form.fields['address'].initial = model.address
        form.fields['telephone'].initial = model.telephone
        form.fields['birthday'].initial = model.birthday
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.request.user.id)
        model.first_name = form.cleaned_data['first_name']
        model.last_name = form.cleaned_data['last_name']
        model.email = form.cleaned_data['email'] 
        model.idnumber = form.cleaned_data['idnumber'] 
        model.fullname = form.cleaned_data['fullname']
        model.postalcode = form.cleaned_data['postalcode']
        model.address = form.cleaned_data['address']
        model.telephone = form.cleaned_data['telephone']
        model.birthday = form.cleaned_data['birthday']
        model.save()
        response = super().form_valid(form)
        if response.status_code == 302:
            if settings.LDAP_SERVER['USE'] and settings.LDAP_SERVER['UPDATE_SERVER']:
                LDAPUpdateUser(self.request.user.username,
                               form.cleaned_data['first_name'],
                               form.cleaned_data['last_name'],
                               form.cleaned_data['email'])
        return response

    def get_success_url(self):
        return reverse_lazy('accounts:profile')

class TokenView(LoginRequiredMixin, generic.View):
    model = CustomUser
    form_class = PasswordForm
    template_name = "accounts/token_view.html"

    def get(self, request, **kwargs):
        form = self.form_class()
        params = {
            'form' : form,
            'brand_name': BrandName()
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        params = {
            'form': form,
            'brand_name': BrandName()
        }
        if form.is_valid():
            password = form.cleaned_data['password']
            if request.user.check_password(password):
                params['refresh'] = RefreshToken.for_user(request.user)
            else:
                params['refresh'] = 'Invalid password'
        return render(request, self.template_name, params)

class UserAddView(LoginRequiredMixin, UserPassesTestMixin, generic.edit.CreateView):
    form_class = UserAddForm
    template_name ="accounts/user_add.html"
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['create_project']:
            CreateUserProject(self.object)
        return response

class UserListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = CustomUser
    template_name = "accounts/user_list.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = CustomUser
    fields = ('first_name', 'last_name', 'email', 'is_superuser', 'is_manager',
              'idnumber', 'fullname', 'postalcode', 'address', 'telephone', 'birthday')
    template_name = "accounts/user_update.html"
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if response.status_code == 302:
            if settings.LDAP_SERVER['USE'] and settings.LDAP_SERVER['UPDATE_SERVER']:
                model = self.model.objects.get(pk=self.kwargs['pk'])
                LDAPUpdateUser(model.username,
                               form.cleaned_data['first_name'],
                               form.cleaned_data['last_name'],
                               form.cleaned_data['email'])
        return response

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = CustomUser
    template_name = "accounts/user_delete.html"
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

class UserUploadView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    model = CustomUser
    form_class = UserUploadForm
    template_name = "accounts/user_upload.html"
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = BrandName()
        return context

    def form_valid(self, form):
        csvfile = io.TextIOWrapper(form.cleaned_data['csv_file'])
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            try:
                user = self.model.objects.get(username=row[0])
                if user.first_name != row[1]:
                    user.first_name = row[1]
                if user.last_name != row[2]:
                    user.last_name = row[2]
                if user.email != row[3]:
                    user.email = row[3]
                if user.idnumber != row[4]:
                    user.idnumber = row[4]
                if user.fullname != row[5]:
                    user.fullname = row[5]
                if user.postalcode != row[6]:
                    user.postalcode = row[6]
                if user.address != row[7]:
                    user.address = row[7]
                if user.telephone != row[8]:
                    user.telephone = row[8]
                birthday = datetime.datetime.strptime(row[9], UserUploadDateFormat)
                if user.birthday != birthday:
                    user.birthday = birthday
                user.save()
            except:
                if len(row[10]) >= 8:
                    birthday = datetime.datetime.strptime(row[9], UserUploadDateFormat)
                    password = make_password(row[10])
                    user = self.model.objects.create(
                        username=row[0],
                        first_name=row[1],
                        last_name=row[2],
                        email=row[3],
                        idnumber=row[4],
                        fullname=row[5],
                        postalcode=row[6],
                        address=row[7],
                        telephone=row[8],
                        birthday=birthday,
                        password=password)
                    if form.cleaned_data['create_project']:
                        CreateUserProject(user)
        return super().form_valid(form)

class UserDownloadView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        now = datetime.datetime.now()
        filename = 'User_%s.csv' % (now.strftime('%Y%m%d_%H%M%S'))
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        writer = csv.writer(response)
        writer.writerow(['Username', 'Firstname', 'Lastname', 'Email',
                         'IDNumber', 'FullName', 'PostalCode', 'Address', 'TelephoneNumber',
                         'Birthday', 'InitialPassword'])
        for user in CustomUser.objects.all():
            if user.birthday:
                birthday = user.birthday.strftime(UserUploadDateFormat)
            else:
                birthday = ''
            writer.writerow([user.username, user.first_name, user.last_name, user.email,
                             user.idnumber, user.fullname, user.postalcode, user.address,
                             user.telephone, birthday, ' '])
        return response

# class UserCloneView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
#     model = CustomUser
#     form_class = UserCloneForm
#     template_name = "accounts/user_clone.html"
#     list_name = 'accounts:api_user_list'
#     success_url = reverse_lazy('accounts:user_list')
#
#     def test_func(self):
#         return self.request.user.is_superuser
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['brand_name'] = BrandName()
#         return context
#
#     def create_user(self, user):
#         models = self.model.objects.filter(username=user['username'])
#         if len(models) == 0:
#             self.model.objects.create(
#                 username=user['username'], password=user['password'],
#                 first_name=user['first_name'], last_name=user['last_name'],
#                 email=user['email'], is_superuser=user['is_superuser'],
#                 is_manager=user['is_manager']
#             )
#
#     def form_valid(self, form):
#         if form.access is not None:
#             rooturl = form.cleaned_data['url'].rstrip('/')
#             url = '%s%s' % (rooturl, reverse(self.list_name))
#             headers = {'Authorization': 'JWT %s' % (form.access)}
#             response = requests.get(url, headers=headers)
#             if response.status_code == 200:
#                 for user in response.json():
#                     self.create_user(user)
#         return super().form_valid(form)

# API
# class ListAPIView(generics.ListAPIView):
#     permission_classes = (IsAuthenticated, IsAdminUser)
#     model = CustomUser
#     serializer_class = UserSerializer
#
#     def get_queryset(self):
#         return self.model.objects.all()

# class RetrieveAPIView(generics.RetrieveAPIView):
#     permission_classes = (IsAuthenticated, IsAdminUser)
#     model = CustomUser
#     serializer_class = UserSerializer
#     lookup_field = 'pk'
#
#     def get_queryset(self):
#         return self.model.objects.all()
