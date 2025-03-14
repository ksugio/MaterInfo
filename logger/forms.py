from django import forms
from .models import Logger

class LoggerAddForm(forms.ModelForm):
    class Meta:
        model = Logger
        fields = ('title', 'note', 'host', 'port', 'database',
                  'password', 'interval')
        widgets = {
            'password': forms.PasswordInput()
        }

class LoggerUpdateForm(forms.ModelForm):
    class Meta:
        model = Logger
        fields = ('title', 'status', 'note', 'host', 'port', 'database',
                  'password', 'interval')
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

class LoggerGrabForm(forms.Form):
    start = forms.DateTimeField(label='Start', required=True)
    period = forms.IntegerField(label='Period', required=True)
    sample = forms.ChoiceField(label='Sample')
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
