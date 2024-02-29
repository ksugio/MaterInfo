from django import forms
from .models import Density

class DensityAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Density
        fields = ('title', 'note', 'prefix', 'unit', 'measured', 'theoretical')

class DensityUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Density
        fields = ('title', 'status', 'note', 'prefix', 'unit', 'measured', 'theoretical')
