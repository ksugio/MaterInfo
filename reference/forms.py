from django import forms
from project.forms import ClearableFileInput
from .models import Article

class ArticleUpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'author', 'journal', 'volume', 'year', 'page', 'url', 'file', 'type', 'note')
        widgets = {
            'file': ClearableFileInput(),
        }
