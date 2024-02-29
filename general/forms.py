from django import forms
from .models import General

class GeneralAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = General
        fields = ('title', 'note', 'prefix', 'category', 'value')

class GeneralUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = General
        fields = ('title', 'status', 'note', 'prefix', 'category', 'value')
