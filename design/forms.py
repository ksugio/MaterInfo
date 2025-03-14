from django import forms
from .models.experiment import Experiment, AcquisitionChoices
from .models.condition import Condition
from .models.design import Design

class DesignAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Property Prefix')

    class Meta:
        model = Design
        fields = ('title', 'note', 'ngen', 'prefix', 'modelfunc')

class DesignUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Property Prefix')

    class Meta:
        model = Design
        fields = ('title', 'status', 'note', 'ngen', 'prefix', 'modelfunc')

class ConditionAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Condition
        fields = ('prefix', 'mode', 'values')

class ConditionUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Condition
        fields = ('prefix', 'mode', 'values')

class ExperimentAddForm(forms.ModelForm):
    dispcond = forms.CharField(label='Condition', widget=forms.Textarea, required=True)

    class Meta:
        model = Experiment
        fields = ('title', 'dispcond', 'property', 'note')

class ExperimentUpdateForm(forms.ModelForm):
    dispcond = forms.CharField(label='Condition', widget=forms.Textarea, required=True)

    class Meta:
        model = Experiment
        fields = ('title', 'dispcond', 'property', 'note')

class BayesianForm(forms.ModelForm):
    acquisition = forms.ChoiceField(label='Acquisition Function', choices=AcquisitionChoices, initial=0)
    target = forms.FloatField(label='Target Property', required=True)

    class Meta:
        model = Experiment
        fields = ('title', 'acquisition', 'target', 'note')

class AddSampleForm(forms.Form):
    title = forms.CharField(label='Title')
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
