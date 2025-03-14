from django import forms
from project.forms import ClearableFileInput
from .models import File

class MDFileForm(forms.Form):
    md_file = forms.FileField(label='MD File', required=True)

class FileUpdateForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('title', 'note', 'file')
        widgets = {
            'file': ClearableFileInput(),
        }
