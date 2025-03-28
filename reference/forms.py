from django import forms
from project.forms import ClearableFileInput
from .models.article import Article
from .models.text import Text
from .models.translate import Translate
from .models.clip import Clip

class DOIForm(forms.Form):
    doi = forms.CharField(label='DOI', max_length=256, required=True,
                          widget=forms.Textarea(attrs={'rows': 2, 'cols': 64}))

class BibtexForm(forms.Form):
    file = forms.fields.FileField(label='File')

class ZipForm(forms.Form):
    file = forms.fields.FileField(label='File')

class ArticleUpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('type', 'key', 'title', 'author', 'journal', 'volume', 'number',
                  'month', 'year', 'pages', 'cited', 'impact', 'booktitle',
                  'publisher', 'address', 'doi', 'url', 'file', 'abstract', 'note')
        widgets = {
            'file': ClearableFileInput(),
        }

class TextUpdateForm(forms.ModelForm):
    re_extract = forms.fields.BooleanField(label='Re-extract text', required=False, initial=False)

    class Meta:
        model = Text
        fields = ('title', 'note', 'start', 'end')

class TranslateAddForm(forms.ModelForm):
    api_key = forms.CharField(label='API Key', required=True,
                              widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))

    class Meta:
        model = Translate
        fields = ('title', 'note', 'translate', 'sourcel', 'targetl', 'api_key')

class TranslateUpdateForm(forms.ModelForm):
    api_key = forms.CharField(label='API Key', required=False,
                              widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))
    re_extract = forms.fields.BooleanField(label='Re-extract text', required=False, initial=False)

    class Meta:
        model = Translate
        fields = ('title', 'note', 'translate', 'sourcel', 'targetl', 'api_key', 're_extract')

class ClipUpdateForm(forms.ModelForm):
    re_extract = forms.fields.BooleanField(label='Re-extract text', required=False, initial=False)

    class Meta:
        model = Clip
        fields = ('title', 'note', 'start', 'end')