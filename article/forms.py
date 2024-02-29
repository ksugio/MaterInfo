from django import forms
from mdeditor.widgets import MDEditorWidget
from project.forms import ClearableFileInput
from .models import Article, File

class AddForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'category', 'public', 'text')
        widgets = { 'text' : MDEditorWidget }

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'status', 'category', 'public', 'text')
        widgets = { 'text' : MDEditorWidget }

class MDFileForm(forms.Form):
    md_file = forms.FileField(label='MD File', required=True)

class FileUpdateForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('title', 'note', 'file')
        widgets = {
            'file': ClearableFileInput(),
        }
