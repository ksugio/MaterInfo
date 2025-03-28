from django import forms
from project.forms import ClearableFileInput
from .models import File

class UploadForm(forms.Form):
    file = forms.FileField(label='File', required=True)
    comment = forms.CharField(label='Comment', widget=forms.Textarea(), initial='Upload', required=True)

class TranslateForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    comment = forms.CharField(label='Comment', required=False, widget=forms.Textarea())
    TranslateChoices = ((0, 'DeepL API Free'), (1, 'DeepL API'))
    translate = forms.ChoiceField(label='Translate', choices=TranslateChoices, initial=0)
    sourcel = forms.CharField(label='Source Language', max_length=10, initial='JA')
    targetl = forms.CharField(label='Target Language', max_length=10, initial='EN')
    api_key = forms.CharField(label='API Key', required=True,
                              widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))

class FileAddForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        if not file and not url:
            raise forms.ValidationError("File or URL is required.")

    class Meta:
        model = File
        fields = ('name', 'note', 'file', 'url', 'svg2pdf')
        widgets = {
            'url': forms.Textarea(attrs={'cols': '100', 'rows': '1'})
        }

class FileUpdateForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        if not file and not url:
            raise forms.ValidationError("File or URL is required.")

    class Meta:
        model = File
        fields = ('name', 'note', 'file', 'url', 'svg2pdf')
        widgets = {
            'file': ClearableFileInput(),
            'url': forms.Textarea(attrs={'cols': '100', 'rows': '1'})
        }
