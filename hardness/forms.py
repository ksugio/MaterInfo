from django import forms
from .models import Hardness

class HardnessAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Hardness
        fields = ('title', 'note', 'prefix', 'unit', 'load', 'load_unit', 'time')

class HardnessUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Hardness
        fields = ('title', 'status', 'note', 'prefix', 'unit', 'load', 'load_unit', 'time')
