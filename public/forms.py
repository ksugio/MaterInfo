from django import forms
from .models import Public

class PublicForm(forms.ModelForm):
    class Meta:
        model = Public
        fields = ('article',)


