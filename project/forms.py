from django import forms
from .views.requests import GetAccessToken, GetSessionAccessToken, SetSessionRefreshToken, VerifyID, ParseURL
from .models import Project

class AliasForm(forms.Form):
    template = forms.ChoiceField(label='Template', required=True)

class CSVFileForm(forms.Form):
    csv_file = forms.FileField(label='CSV File', required=True)

class CloneForm(forms.Form):
    url = forms.CharField(label='URL', max_length=256, required=True,
                          widget=forms.Textarea(attrs={'rows':2, 'cols':64}))
    token = forms.CharField(label='Token', max_length=1024, required=False, widget=forms.HiddenInput)
    retrieve_name = None
    viwe_name = None
    view_args = 1
    session = None
    access = None
    host = None
    auth = ''

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['url'].startswith(self.host):
            self.auth = 'Cookie'
        else:
            rooturl, id, _ = ParseURL(cleaned_data['url'], self.view_name, self.view_args)
            access = GetSessionAccessToken(rooturl, self.session)
            if access == 'InvalidToken':
                self.fields['token'].widget = forms.Textarea(attrs={'rows':5, 'cols':64})
                raise forms.ValidationError("Input Token.")
            elif access == 'NoToken':
                refresh = cleaned_data['token']
                if refresh:
                    access = GetAccessToken(rooturl, refresh)
                    if access is None:
                        self.fields['token'].widget = forms.Textarea(attrs={'rows': 5, 'cols': 64})
                        raise forms.ValidationError("Input Token.")
                    data = VerifyID(rooturl, self.retrieve_name, access, id)
                    if data is None:
                        raise forms.ValidationError("Invalid ID (%d)." % (id))
                    self.auth = 'JWT'
                    self.access = access
                    SetSessionRefreshToken(rooturl, self.session, refresh)
                else:
                    self.fields['token'].widget = forms.Textarea(attrs={'rows': 5, 'cols': 64})
                    raise forms.ValidationError("Input Token.")
            else:
                self.auth = 'JWT'
                self.access = access

class ImportForm(CloneForm):
    lower = forms.BooleanField(label='Import Lower', required=False)

class SetRemoteForm(CloneForm):
    pass

class TokenForm(forms.Form):
    url = forms.CharField(label='URL', max_length=256, required=True,
                          widget = forms.Textarea(attrs={'rows': 2, 'cols': 64}))
    token = forms.CharField(label='Token', max_length=1024, required=True,
                            widget=forms.Textarea(attrs={'rows': 5, 'cols': 64}))
    session = None
    refresh = None
    access = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].widget.attrs['readonly'] = 'readonly'

    def clean(self):
        cleaned_data = super().clean()
        rooturl = cleaned_data['url']
        refresh = cleaned_data['token']
        access = GetAccessToken(rooturl, refresh)
        if access is None:
            raise forms.ValidationError("Invalid Token.")
        self.refresh = refresh
        self.access = access
        SetSessionRefreshToken(rooturl, self.session, refresh)

class ClearableFileInput(forms.ClearableFileInput):
    template_name = 'project/clearable_file_input.html'

class SearchForm(forms.Form):
    string = forms.CharField(label='String')
    condition = forms.ChoiceField(label='Condition', choices=((0, 'OR'), (1, 'AND')), initial=0)
    lower = forms.BooleanField(label='Search Lower', initial=True, required=False)
    order = forms.ChoiceField(label='Order', choices=((0, 'New'), (1, 'Old')), initial=0)

class RestartDaemonForm(forms.Form):
    process = forms.ChoiceField(label='Process', required=True)

class ProjectAddForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'note', 'member')
        widgets = {
            'member': forms.CheckboxSelectMultiple(),
        }

class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'status', 'note', 'member')
        widgets = {
            'member': forms.CheckboxSelectMultiple(),
        }