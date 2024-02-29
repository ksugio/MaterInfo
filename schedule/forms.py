from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ('title', 'start', 'finish', 'complete', 'person', 'note')

    def clean(self):
        cleaned_data = super().clean()
        start_dt = cleaned_data.get("start")
        finish_dt = cleaned_data.get("finish")
        comp_dt = cleaned_data.get("complete")
        if finish_dt < start_dt:
            raise forms.ValidationError("Finish time should be greater than start time.")
        if comp_dt < 0 or comp_dt > 100:
            raise forms.ValidationError('Input value from 0 to 100.')

