from django import forms
from project.forms import ClearableFileInput
from .models import Material

class MaterialAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Material
        fields = ('title', 'note', 'prefix', 'fraction', 'file', 'percent_in', 'template')

class MaterialUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Material
        fields = ('title', 'status', 'note', 'prefix', 'fraction', 'file', 'percent_in', 'template')
        widgets = {
            'file': ClearableFileInput(),
        }

