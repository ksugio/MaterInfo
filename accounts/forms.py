from django import forms
from django.contrib.auth.forms import UserCreationForm
from project.views.token import GetAccessToken
from .models import CustomUser

class UserAddForm(UserCreationForm):
    create_project = forms.BooleanField(label='Create user project', initial=False, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_superuser',
                  'is_manager', 'idnumber', 'fullname', 'postalcode', 'address', 'telephone', 'birthday')

class UserUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV File', required=True)
    create_project = forms.BooleanField(label='Create user project', initial=False, required=False)

class UserCloneForm(forms.Form):
    url = forms.CharField(label='URL', max_length=300, required=True,
                          widget=forms.Textarea(attrs={'rows':2, 'cols':64}))
    token = forms.CharField(label='Token', max_length=1024, required=True,
                            widget=forms.Textarea(attrs={'rows': 5, 'cols': 64}))
    refresh = None
    access = None

    def clean(self):
        cleaned_data = super().clean()
        rooturl = cleaned_data['url'].rstrip('/')
        refresh = cleaned_data['token']
        access = GetAccessToken(rooturl, refresh)
        if access is None:
            raise forms.ValidationError("Access failed, check URL or token.")
        self.refresh = refresh
        self.access = access

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=150, required=False)
    last_name = forms.CharField(label='Last Name', max_length=150, required=False)
    email = forms.CharField(label='Email address', max_length=254, required=True)
    idnumber = forms.CharField(label='ID Number', max_length=30, required=False)
    fullname = forms.CharField(label='Full Name', max_length=100, required=False)
    postalcode = forms.CharField(label='Postal Code', max_length=10, required=False)
    address = forms.CharField(label='Address', max_length=200, required=False)
    telephone = forms.CharField(label='Telephone Number', max_length=16, required=False)
    birthday = forms.DateField(label='Birthday', required=False)

class PasswordForm(forms.Form):
    password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput, required=True)
