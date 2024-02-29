from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ('title', 'start', 'finish', 'note')

    def clean(self):
        cleaned_data = super().clean()
        start_dt = cleaned_data.get("start")
        finish_dt = cleaned_data.get("finish")
        if finish_dt < start_dt:
            raise forms.ValidationError("Finish time should be greater than start time.")
